import logging
import pickle
from copy import deepcopy
from dataclasses import dataclass

import asyncpg
import pytz

from .notifications import NotificationType


@dataclass
class SubscriptionOptions:
    """A dataclass for holding channel subscription options."""

    notification_type: NotificationType
    launch_mentions: str
    timezone: str


class DataStore:
    """A class to handle storing bot data.

    Must a database connection pool from asyncpg.create_pool.

    In-memory stateful data is stored by serializing and loading from a file,
    subscribed channels data is stored in a postgres database.

    All methods that either return or take mutable objects as parameters make a deep
    copy of said object(s) so that changes cannot be made outside the instance.

    Immutable object references:
    - https://stackoverflow.com/a/23715872/6396652
    - https://stackoverflow.com/a/986145/6396652
    """

    def __init__(self, db_pool: asyncpg.Pool, pickle_file_path: str):
        self._pickle_file_path = pickle_file_path
        self.db_pool = db_pool

        # Boolean indicating if a launch notification has been sent for the current
        # schedule.
        self._launch_embed_for_current_schedule_sent: bool = False
        # A dict of the most previously sent schedule embed (for diffing).
        self._previous_schedule_embed_dict: dict = {}

        try:
            with open(self._pickle_file_path, "rb") as f_in:
                tmp = pickle.load(f_in)
                self.__dict__.update(tmp)
            logging.info(f"Updated self.__dict__ from {self._pickle_file_path}")
        except FileNotFoundError:
            logging.info(f"Could not find file at location: {self._pickle_file_path}")

    def save_state(self) -> None:
        # Idea from https://stackoverflow.com/a/2842727/6396652.
        # pylint: disable=line-too-long
        to_dump = {
            "_launch_embed_for_current_schedule_sent": self._launch_embed_for_current_schedule_sent,
            "_previous_schedule_embed_dict": self._previous_schedule_embed_dict,
        }
        with open(self._pickle_file_path, "wb") as f_out:
            pickle.dump(to_dump, f_out, protocol=pickle.HIGHEST_PROTOCOL)

    def get_notification_task_vars(self) -> tuple[bool, dict]:
        return (
            self._launch_embed_for_current_schedule_sent,
            deepcopy(self._previous_schedule_embed_dict),
        )

    def set_notification_task_vars(
        self,
        launch_embed_for_current_schedule_sent: bool,
        previous_schedule_embed_dict: dict,
    ) -> None:
        self._launch_embed_for_current_schedule_sent = (
            launch_embed_for_current_schedule_sent
        )
        self._previous_schedule_embed_dict = deepcopy(previous_schedule_embed_dict)
        self.save_state()

    # pylint: disable=too-many-positional-arguments
    async def add_subbed_channel(
        self,
        channel_id: str,
        channel_name: str,
        guild_id: str,
        notif_type: NotificationType,
        launch_mentions: str | None,
        timezone: str | None = None,
    ) -> bool:
        """Add a channel to subscribed channels.

        Args:
            channel_id: The channel to add.
            channel_name: The name of the channel.
            guild_id: The guild the channel is in.
            notif_type: The type of subscription.
            launch_mentions: The mentions for launch notifications.
            timezone: The timezone to use for launch times.

        Returns:
            A bool indicating if the channel was added or not.

        """
        notification_type = notif_type.name
        sql = """
            insert into subscribed_channels
            (channel_id, guild_id, channel_name, notification_type, launch_mentions, timezone)
            values
            ($1, $2, $3, $4, $5, $6);"""
        async with self.db_pool.acquire() as conn:
            try:
                response = await conn.execute(
                    sql,
                    channel_id,
                    guild_id,
                    channel_name,
                    notification_type,
                    launch_mentions,
                    timezone or "UTC",
                )
                # Not great practice but it works.
                if response == "INSERT 0 1":
                    return True
            except asyncpg.exceptions.UniqueViolationError:
                # channel_id (primary key) already exists.
                pass
        return False

    async def get_subbed_channels(self) -> dict[int, SubscriptionOptions]:
        channels = {}
        sql = "select * from subscribed_channels;"
        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(sql)
            for rec in records:
                cid = int(rec["channel_id"])
                notif_type = rec["notification_type"]
                mentions = (
                    rec["launch_mentions"] if rec["launch_mentions"] is not None else ""
                )
                timezone = rec.get("timezone", "UTC") if rec.get("timezone") else "UTC"
                channels[cid] = SubscriptionOptions(NotificationType[notif_type], mentions, timezone)
        return channels

    async def remove_subbed_channel(self, channel_id: str) -> bool:
        sql = "delete from subscribed_channels where channel_id = $1;"
        async with self.db_pool.acquire() as conn:
            response = await conn.execute(sql, channel_id)
            if response == "DELETE 1":
                return True
        return False

    async def update_channel_timezone(self, channel_id: str, timezone: str) -> bool:
        """Update the timezone for a subscribed channel.

        Args:
            channel_id: The channel to update.
            timezone: The timezone to set.

        Returns:
            A bool indicating if the channel was updated.
        """
        sql = "update subscribed_channels set timezone = $1 where channel_id = $2;"
        async with self.db_pool.acquire() as conn:
            response = await conn.execute(sql, timezone, channel_id)
            if response == "UPDATE 1":
                return True
        return False

    async def get_channel_timezone(self, channel_id: str) -> str:
        """Get the timezone for a channel.

        Args:
            channel_id: The channel to get timezone for.

        Returns:
            The timezone string, defaults to UTC if not set.
        """
        sql = "select timezone from subscribed_channels where channel_id = $1;"
        async with self.db_pool.acquire() as conn:
            record = await conn.fetchrow(sql, channel_id)
            if record and record.get("timezone"):
                return record["timezone"]
            return "UTC"

    async def subbed_channels_count(self) -> int:
        sql = "select count(*) from subscribed_channels;"
        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(sql)
            return int(records[0]["count"])

    async def register_metric(self, action: str, guild_id: str) -> bool:
        """Register an action occurring to the metrics table.

        Args:
            action: The name of the action, naming convention is camel_case.
            guild_id: The ID of the guild the action occurred in.

        Returns:
            A bool indicating if the metric was registered or not.

        """
        sql = """
            insert into metrics
            (action, guild_id)
            values
            ($1, $2);"""
        async with self.db_pool.acquire() as conn:
            response = await conn.execute(
                sql,
                action,
                guild_id,
            )
            if response == "INSERT 0 1":
                return True
        return False

    async def update_counts(self, guild_count: int) -> bool:
        """Insert new guild and subscribed channel counts into the db.

        Args:
            guild_count: The number of guilds the bot is currently in.

        Returns:
            A bool indicating if the count was added or not.

        """
        subbed_count = await self.subbed_channels_count()

        sql = """
            insert into counts
            (guild_count, subscribed_count)
            values
            ($1, $2);"""
        async with self.db_pool.acquire() as conn:
            response = await conn.execute(
                sql,
                guild_count,
                subbed_count,
            )
            if response == "INSERT 0 1":
                return True
        return False

    async def day_old_counts(self) -> tuple[int, int]:
        """Get guild and subsribed count from 24 hours ago.

        Returns:
            guild count, subscribed channel count
        """
        sql = """
            select
                guild_count,
                subscribed_count
            from
                counts
            where
                time between now() - interval '1 day' and now()
            order by
                time asc
            limit
                1;"""
        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(sql)
            try:
                record = records[0]
                return int(record["guild_count"]), int(record["subscribed_count"])
            except (IndexError, ValueError, KeyError):
                return 0, 0


def convert_time_to_timezone(date_string: str, timezone_str: str) -> str:
    """Convert a UTC datetime string to a specified timezone.

    Args:
        date_string: ISO format datetime string in UTC.
        timezone_str: Target timezone name (e.g., 'America/New_York').

    Returns:
        Formatted datetime string in the target timezone.
    """
    if date_string is None:
        return "To Be Announced"
    
    try:
        # Parse the UTC datetime
        utc_dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        
        # Convert to target timezone
        if timezone_str and timezone_str != "UTC":
            target_tz = pytz.timezone(timezone_str)
            local_dt = utc_dt.astimezone(target_tz)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, pytz.exceptions.UnknownTimeZoneError):
        # Fallback to UTC if timezone is invalid
        utc_dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
