"""Redis structure
---------------
All keys are prepended with "slb."

Key                     | Value
------------------------|---------------------------------------------------------------
subscribed_channels     | A Redis SET of channel IDs that are to be sent notifications
str(Guild ID)           | A string containing Discord mentions (channels, users, etc.)
metrics                 | A Redis hash containing these fields:
                        | "totalCommands" - Total number of commands issued by users
notification_task_store | A Redis hash containing variables that need to persist between
                        | runs of bgtasks.notification_task. This includes:
                        | "ls_notif_sent" = "True" OR "False" (str not bool)
                        | "li_embed_dict" = pickled(embed_dict)
                        | See bgtasks.notification_task to see how each var is used
"""

from aredis import StrictRedis
import logging, pickle

from config import REDIS_HOST, REDIS_PORT, REDIS_DB
from statics import general_error_embed


class RedisClient(StrictRedis):
    def __init__(self, host, port, db_num):
        super().__init__(host=host, port=port, db=db_num)

        self.log = logging.getLogger(__name__)
        self.log.info(f"Connected to Redis at {host}:{port} on DB {db_num}")

    async def init_defaults(self):
        """If the database is new, create default values for needed keys
        """
        if not await self.exists("slb.notification_task_store"):
            self.log.debug("slb.notification_task_store hash does not exist, creating")
            await self.set_notification_task_store("False", general_error_embed)

    async def get_notification_task_store(self):
        """Gets and decodes / deserializes variables from notification_task_store
        Returns a list with these indexes:
        0: ls_notif_sent
        1: li_embed_dict
        """
        hash_key = "slb.notification_task_store"

        ls_notif_sent = await self.hget(hash_key, "ls_notif_sent")
        li_embed_dict = await self.hget(hash_key, "li_embed_dict")

        return (ls_notif_sent.decode("UTF-8"), pickle.loads(li_embed_dict))

    async def set_notification_task_store(self, ls_notif_sent, li_embed_dict):
        """Update / create the hash for notification_task_store
        Automatically encodes / serializes both arguments
        """
        hash_key = "slb.notification_task_store"

        ls_notif_sent = ls_notif_sent.encode("UTF-8")
        li_embed_dict = pickle.dumps(li_embed_dict, protocol=pickle.HIGHEST_PROTOCOL)

        await self.hset(hash_key, "ls_notif_sent", ls_notif_sent)
        await self.hset(hash_key, "li_embed_dict", li_embed_dict)

    async def set_guild_mentions(self, guild_id, to_mention):
        """Set mentions for a guild
        guild_id can be int or str
        to_mention should be an string of roles / tags / etc.
        """
        guild_mentions_db_key = f"slb.{str(guild_id)}"
        to_mention = to_mention.encode("UTF-8")
        await self.set(guild_mentions_db_key, to_mention)

    async def get_guild_mentions(self, guild_id):
        """Returns a string of mentions for that guild
        guild_id can be int or str
        returns False if guild_id does not have any settings stored
        """
        guild_mentions_db_key = f"slb.{str(guild_id)}"
        if not await self.exists(guild_mentions_db_key):
            return False
        to_mention = await self.get(guild_mentions_db_key)
        return to_mention.decode("UTF-8")

    async def delete_guild_mentions(self, guild_id):
        """Deletes all mentions for the given guild_id
        guild_id can be int or str
        Returns the number of keys that were deleted
        """
        guild_mentions_db_key = f"slb.{str(guild_id)}"
        return await redis.delete(guild_mentions_db_key)


# This is the instance that will be imported and used by all other files
redis = RedisClient(REDIS_HOST, REDIS_PORT, REDIS_DB)
