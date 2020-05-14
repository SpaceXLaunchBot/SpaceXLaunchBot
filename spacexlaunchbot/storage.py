import pickle  # nosec
from typing import Tuple, Set, Dict

from sqlitedict import SqliteDict

import config


class SqliteDb:
    """Database key/value structure (all keys are prepended with KEY_PREFIX):
    ------------------------|-------------------------------------------------
    subscribed_channels     | A set of channel IDs to be sent notifications.
    guild:{guild_id}        | A string of channels, users, etc. to ping for a
                            | "launching soon" message.
    notification_task_store | A list containing variables that need to persist
                            | between runs of the notification task.
                            | See set_notification_task_store for details.
                            | See bgtasks for usage.

    """

    KEY_PREFIX = "slb:"
    KEY_SUBSCRIBED_CHANNELS = KEY_PREFIX + "subscribed_channels"
    KEY_NOTIFICATION_TASK_STORE = KEY_PREFIX + "notification_task_store"
    KEY_GUILD = KEY_PREFIX + "guild:{}"

    def __init__(self, sqlite_location: str):
        self.sqlite = SqliteDict(sqlite_location, autocommit=False)

    def init_defaults(self) -> None:
        """Create default values for non existent required keys"""
        if self.KEY_NOTIFICATION_TASK_STORE not in self.sqlite:
            self.sqlite[self.KEY_NOTIFICATION_TASK_STORE] = [False, ""]

        if self.KEY_SUBSCRIBED_CHANNELS not in self.sqlite:
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = set()

        self.sqlite.commit()

    def get_notification_task_store(self) -> Tuple[bool, Dict]:
        """Gets and decodes / deserializes variables from notification_task_store.

        Returns:
            A list with these indexes:
                0: ls_notif_sent: True/False if the launching soon msg has been sent.
                1: li_embed_dict: The latest launch info embed as a dictionary.

        """
        return self.sqlite[self.KEY_NOTIFICATION_TASK_STORE]

    def set_notification_task_store(
        self, ls_notif_sent: bool, li_embed_dict: Dict
    ) -> None:
        """Update / create the hash for notification_task_store.

        Args:
            ls_notif_sent: True/False if the launching soon msg has been sent.
            li_embed_dict: The latest launch info embed as a dictionary.

        """
        self.sqlite[self.KEY_NOTIFICATION_TASK_STORE] = [ls_notif_sent, li_embed_dict]
        self.sqlite.commit()

    def set_guild_mentions(self, guild_id: int, to_mention: str) -> None:
        """Set mentions for a guild.

        Args:
            guild_id: A discord.Guild ID.
            to_mention: A string of Discord mentions; names, roles, tags, etc.

        """
        self.sqlite[self.KEY_GUILD.format(guild_id)] = to_mention
        self.sqlite.commit()

    def get_guild_mentions(self, guild_id: int) -> str:
        """Get mentions for a guild.

        Args:
            guild_id: A discord.Guild ID.

        Returns:
            A string of Discord mentions; names, roles, tags, etc OR empty string.

        """
        return self.sqlite.get(self.KEY_GUILD.format(guild_id), "")

    def delete_guild_mentions(self, guild_id: int) -> int:
        """Delete mentions for a guild.

        Args:
            guild_id: A discord.Guild ID.

        Returns:
            0 if nothing was removed, 1 if the mentions were removed.

        """
        if self.KEY_GUILD.format(guild_id) in self.sqlite:
            del self.sqlite[self.KEY_GUILD.format(guild_id)]
            self.sqlite.commit()
            return 1
        return 0

    def get_subbed_channels(self) -> Set[int]:
        """Get all channel IDs contained in the subscribed_channels set.

        Returns:
            A set of integers representing discord.Channel IDs.

        """
        return self.sqlite[self.KEY_SUBSCRIBED_CHANNELS]

    def add_subbed_channel(self, channel_id: int) -> int:
        """Add a channel to the subscribed_channels set.

        Args:
            channel_id: A discord.Channel ID.

        Returns:
            0 if nothing was added, 1 if the channel was added.

        """
        # Checks membership purely for determining return value.
        channels = self.sqlite[self.KEY_SUBSCRIBED_CHANNELS]
        if channel_id not in channels:
            channels.add(channel_id)
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = channels
            self.sqlite.commit()
            return 1
        return 0

    def remove_subbed_channel(self, channel_id: int) -> int:
        """Remove a channel from the subscribed_channels set.

        Args:
            channel_id: A discord.Channel ID.

        Returns:
            0 if nothing was removed, 1 if the channel was removed.

        """
        # Checks membership purely for determining return value.
        channels = self.sqlite[self.KEY_SUBSCRIBED_CHANNELS]
        if channel_id in channels:
            channels.remove(channel_id)
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = channels
            self.sqlite.commit()
            return 1
        return 0

    def remove_subbed_channels(self, channels_to_remove: Set[int]) -> None:
        """Remove a set of channels from the subscribed_channels set.

        Args:
            channels_to_remove: A set of discord.Channel IDs.

        """
        self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = (
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] - channels_to_remove
        )
        self.sqlite.commit()

    def subbed_channels_count(self) -> int:
        """Get the size of the subscribed_channels set."""
        return len(self.sqlite[self.KEY_SUBSCRIBED_CHANNELS])

    def stop(self):
        """Closes the database"""
        self.sqlite.commit()
        self.sqlite.close()


class DataStore:
    def __init__(self):
        self.subscribed_channels = []
        self.launching_soon_notif_sent = False
        self.launch_information = {}
        self.guild_options = {}

        self._load()

    def _load(self):
        with open(config.PICKLE_DUMP_LOCATION, "rb") as f:
            tmp = pickle.load(f)  # nosec
        self.__dict__.update(tmp)

    def _save(self):
        # Idea from https://stackoverflow.com/a/2842727/6396652.
        with open(config.PICKLE_DUMP_LOCATION, "wb") as f:
            pickle.dump(self.__dict__, f, protocol=pickle.HIGHEST_PROTOCOL)


# This is the instance that will be imported and used by all other files
db = SqliteDb(config.SQLITE_LOCATION)
