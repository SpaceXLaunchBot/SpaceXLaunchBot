import logging
import pickle
import aredis
from typing import Tuple, Set, ByteString

import statics
import config


class RedisClient(aredis.StrictRedis):
    """Redis Structure
    All keys are prepended with "slb:"
    Variables in the keys described below are enclosed in {braces}

    Key                       | Value
    --------------------------|---------------------------------------------------------
    subscribed_channels       | A Redis SET of channel IDs to be sent notifications
    guild:{guild_id}          | A hash containing options for that guild. This includes:
                              | "mentions": String of channels, users, etc. to ping for
                              | a "launching soon" message
    metric:{metric_name}      | Currently not used.
                              | Example use: slb:metric:commands_used
    notification_task_store   | A Redis hash containing variables that need to persist
                              | between runs of the notification task. This includes:
                              | "ls_notif_sent": "True" OR "False" (str not bool)
                              | "li_embed_dict": pickled(embed_dict)
                              | See bgtasks.notification_task to see usage
    """

    def __init__(self, host: str, port: int, db_num: int):
        super().__init__(host=host, port=port, db=db_num)

    async def init_defaults(self):
        """If the database is new, create default values for needed keys
        """
        if not await self.exists("slb:notification_task_store"):
            logging.info("slb:notification_task_store does not exist, creating")
            await self.set_notification_task_store("False", statics.GENERAL_ERROR_EMBED)

    async def get_notification_task_store(self) -> Tuple[str, dict]:
        """Gets and decodes / deserializes variables from notification_task_store
        Returns a list with these indexes:
        0: ls_notif_sent
        1: li_embed_dict
        """
        hash_key = "slb:notification_task_store"

        ls_notif_sent = await self.hget(hash_key, "ls_notif_sent")
        li_embed_dict = await self.hget(hash_key, "li_embed_dict")

        return ls_notif_sent.decode("UTF-8"), pickle.loads(li_embed_dict)

    async def set_notification_task_store(
        self, ls_notif_sent: str, li_embed_dict: dict
    ):
        """Update / create the hash for notification_task_store
        Automatically encodes / serializes both arguments
        """
        hash_key = "slb:notification_task_store"

        ls_notif_sent_bytes = ls_notif_sent.encode("UTF-8")
        li_embed_dict_bytes = pickle.dumps(li_embed_dict)

        await self.hset(hash_key, "ls_notif_sent", ls_notif_sent_bytes)
        await self.hset(hash_key, "li_embed_dict", li_embed_dict_bytes)

    async def set_guild_mentions(self, guild_id: int, to_mention: str):
        """Set mentions for a guild
        to_mention is a string of roles / tags / etc.
        """
        guild_key = f"slb:guild:{guild_id}"
        to_mention_bytes = to_mention.encode("UTF-8")
        await self.hset(guild_key, "mentions", to_mention_bytes)

    async def get_guild_mentions(self, guild_id: int) -> str:
        """Returns a string of mentions for that guild
        """
        guild_key = f"slb:guild:{guild_id}"
        to_mention = await self.hget(guild_key, "mentions")
        if not to_mention:
            # TODO: Is to_mention already an empty string?
            return ""
        return to_mention.decode("UTF-8")

    async def delete_guild_mentions(self, guild_id: int):
        """Deletes all mentions for the given guild_id
        Returns 0 if nothing was removed, 1 if the mentions were removed
        """
        guild_key = f"slb:guild:{guild_id}"
        return await self.hdel(guild_key, "mentions")

    async def get_subbed_channels(self) -> Set[ByteString]:
        """Returns all the members of the subscribed_channels set
        """
        return await self.smembers("slb:subscribed_channels")

    async def add_subbed_channel(self, channel_id: int) -> int:
        """Add a channel ID to the subscribed_channels set
        Returns 0 if nothing was added, 1 if the channel was added
        """
        channel_id_bytes = str(channel_id).encode("UTF-8")
        return await self.sadd("slb:subscribed_channels", channel_id_bytes)

    async def remove_subbed_channel(self, channel_id: int) -> int:
        """Remove a channel ID from the subscribed_channels set
        Returns 0 if nothing was removed, 1 if the channel was removed
        """
        channel_id_bytes = str(channel_id).encode("UTF-8")
        return await self.srem("slb:subscribed_channels", channel_id_bytes)

    async def subbed_channels_count(self) -> int:
        """Returns the number of subscribed channels
        """
        return await self.scard("slb:subscribed_channels")


# This is the instance that will be imported and used by all other files
REDIS = RedisClient(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)
