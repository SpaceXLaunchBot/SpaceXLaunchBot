import logging
from typing import Tuple, Set, List

import aredis

import config


class RedisClient(aredis.StrictRedis):
    """A subclass of aredis.StrictRedis to deal with my specific use case(s)

    All keys are prepended with "slb:".

    Database structure:
    ------------------------|-----------------------------------------------------------
    Key                     | Value
    ------------------------|-----------------------------------------------------------
    subscribed_channels     | A Redis SET of channel IDs to be sent notifications.
    guild:{guild_id}        | A hash containing options for that guild. This includes:
                            | "mentions": String of channels, users, etc. to ping for a
                            | "launching soon" message.
    metric:{metric_name}    | Currently not used. Example use: slb:metric:commands_used
    notification_task_store | A Redis hash containing variables that need to persist
                            | between runs of the notification task. This includes:
                            | "ls_notif_sent": "True" OR "False" (str not bool).
                            | "li_dict_hash": SHA256 hash of li embed dict.
                            | Go to bgtasks to see usage.

    """

    KEY_PREFIX = "slb:"
    KEY_SUBSCRIBED_CHANNELS = KEY_PREFIX + "subscribed_channels"
    KEY_NOTIFICATION_TASK_STORE = KEY_PREFIX + "notification_task_store"
    KEY_GUILD = KEY_PREFIX + "guild:{}"

    def __init__(self, host: str, port: int, db_num: int) -> None:
        super().__init__(host=host, port=port, db=db_num)

    async def init_defaults(self) -> None:
        """If the database is new, create default values for needed keys"""
        if not await self.exists(self.KEY_NOTIFICATION_TASK_STORE):
            logging.info(f"{self.KEY_NOTIFICATION_TASK_STORE} does not exist, creating")
            await self.set_notification_task_store("False", "0")

    async def get_notification_task_store(self) -> Tuple[str, str]:
        """Gets and decodes / deserializes variables from notification_task_store.

        Returns:
            A list with these indexes:
                0: ls_notif_sent
                1: li_dict_hash

        """
        hash_key = self.KEY_NOTIFICATION_TASK_STORE
        pipe = await self.pipeline()

        await pipe.hget(hash_key, "ls_notif_sent")
        await pipe.hget(hash_key, "li_dict_hash")

        ls_notif_sent, li_dict_hash = await pipe.execute()

        return ls_notif_sent.decode("UTF-8"), li_dict_hash.decode("UTF-8")

    async def set_notification_task_store(
        self, ls_notif_sent: str, li_dict_hash: str
    ) -> None:
        """Update / create the hash for notification_task_store.

        Automatically encodes / serializes both arguments.

        Args:
            ls_notif_sent: "True" or "False" if launching soon message has been sent.
            li_dict_hash: A string containing the hash of the launch information dict.

        """
        hash_key = self.KEY_NOTIFICATION_TASK_STORE

        ls_notif_sent_bytes = ls_notif_sent.encode("UTF-8")
        li_dict_hash_bytes = li_dict_hash.encode("UTF-8")

        pipe = await self.pipeline()

        await pipe.hset(hash_key, "ls_notif_sent", ls_notif_sent_bytes)
        await pipe.hset(hash_key, "li_dict_hash", li_dict_hash_bytes)

        await pipe.execute()

    async def set_guild_mentions(self, guild_id: int, to_mention: str) -> None:
        """Set mentions for a guild.

        Args:
            guild_id: A discord.Guild ID.
            to_mention: A string of Discord mentions; names, roles, tags, etc.

        """
        to_mention_bytes = to_mention.encode("UTF-8")
        await self.hset(self.KEY_GUILD.format(guild_id), "mentions", to_mention_bytes)

    async def get_guild_mentions(self, guild_id: int) -> str:
        """Get mentions for a guild.

        Args:
            guild_id: A discord.Guild ID.

        Returns:
            A string of Discord mentions; names, roles, tags, etc.

        """
        to_mention = await self.hget(self.KEY_GUILD.format(guild_id), "mentions")
        if to_mention is None:
            return ""
        return to_mention.decode("UTF-8")

    async def delete_guild_mentions(self, guild_id: int) -> int:
        """Delete mentions for a guild.

        Args:
            guild_id: A discord.Guild ID.

        Returns:
            0 if nothing was removed, 1 if the mentions were removed.

        """
        return await self.hdel(self.KEY_GUILD.format(guild_id), "mentions")

    async def get_subbed_channels(self) -> Set[int]:
        """Get all channel IDs contained in the subscribed_channels set.

        Returns:
            A set of integers representing discord.Channel IDs.

        """
        byte_id_set = await self.smembers(self.KEY_SUBSCRIBED_CHANNELS)
        return set(int(cid) for cid in byte_id_set)

    async def add_subbed_channel(self, channel_id: int) -> int:
        """Add a channel to the subscribed_channels set.

        Args:
            channel_id: A discord.Channel ID.

        Returns:
            0 if nothing was added, 1 if the channel was added.

        """
        channel_id_bytes = str(channel_id).encode("UTF-8")
        return await self.sadd(self.KEY_SUBSCRIBED_CHANNELS, channel_id_bytes)

    async def remove_subbed_channel(self, channel_id: int) -> int:
        """Remove a channel from the subscribed_channels set.

        Args:
            channel_id: A discord.Channel ID.

        Returns:
            0 if nothing was removed, 1 if the channel was removed.

        """
        channel_id_bytes = str(channel_id).encode("UTF-8")
        return await self.srem(self.KEY_SUBSCRIBED_CHANNELS, channel_id_bytes)

    async def remove_subbed_channels(self, channels_to_remove: Set[int]) -> List[int]:
        """Remove a set of channels from the subscribed_channels set.

        Args:
            channels_to_remove: A set of discord.Channel IDs.

        Returns:
            A List of all the srem command returns, e.g. [1, 1, 1, 0].

        """
        pipe = await self.pipeline()

        for channel_id in channels_to_remove:
            channel_id_bytes = str(channel_id).encode("UTF-8")
            await pipe.srem(self.KEY_SUBSCRIBED_CHANNELS, channel_id_bytes)

        return await pipe.execute()

    async def subbed_channels_count(self) -> int:
        """Get the size of the subscribed_channels set."""
        return await self.scard(self.KEY_SUBSCRIBED_CHANNELS)


# This is the instance that will be imported and used by all other files
redis = RedisClient(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)
