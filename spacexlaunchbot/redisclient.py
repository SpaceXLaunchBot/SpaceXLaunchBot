"""Redis structure
---------------
All keys are prepended with "slb."

Key                     | Value
------------------------|---------------------------------------------------------------
subscribed_channels     | A Redis SET of channel IDs that are to be sent notifications
str(Guild ID)           | A string containing Discord mentions (channels, users, etc.)
metrics                 | A Redis hash containing these fields:
                        | "totalCommands" - The total number of commands issued
notification_task_store | A Redis hash containing variables that need to persist between
                        | runs of the notification background task(s). This includes:
                        | "launching_soon_notif_sent" = "True" OR "False" (str not bool)
                        | "latest_launch_info_embed_dict" = pickled(embed_dict)
"""

from aredis import StrictRedis
import logging
import pickle

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
        """Gets and decodes variables from notification_task_store
        """
        launching_soon_notif_sent = await self.hget(
            "slb.notification_task_store", "launching_soon_notif_sent"
        )
        latest_launch_info_embed_dict = await self.hget(
            "slb.notification_task_store", "latest_launch_info_embed_dict"
        )
        return {
            "launching_soon_notif_sent": launching_soon_notif_sent.decode("UTF-8"),
            "latest_launch_info_embed_dict": pickle.loads(
                latest_launch_info_embed_dict
            ),
        }

    async def set_notification_task_store(
        self, launching_soon_notif_sent, latest_launch_info_embed_dict
    ):
        """Update / create the hash for notification_task_store
        Automatically encodes both arguments
        """
        launching_soon_notif_sent = launching_soon_notif_sent.encode("UTF-8")
        latest_launch_info_embed_dict = pickle.dumps(
            latest_launch_info_embed_dict, protocol=pickle.HIGHEST_PROTOCOL
        )
        await self.hset(
            "slb.notification_task_store",
            "launching_soon_notif_sent",
            launching_soon_notif_sent,
        )
        await self.hset(
            "slb.notification_task_store",
            "latest_launch_info_embed_dict",
            latest_launch_info_embed_dict,
        )

    async def set_guild_mentions(self, guildID, rolesToMention):
        """Set mentions for a guild
        guildID can be int or str
        rolesToMention should be an string of roles / tags / etc.
        """
        guild_mentions_db_key = f"slb.{str(guildID)}"
        rolesToMention = rolesToMention.encode("UTF-8")
        await self.set(guild_mentions_db_key, rolesToMention)

    async def get_guild_mentions(self, guildID):
        """Returns a string of mentions for that guild
        guildID can be int or str
        returns False if guildID does not have any settings stored
        """
        guild_mentions_db_key = f"slb.{str(guildID)}"
        if not await self.exists(guild_mentions_db_key):
            return False
        rolesToMention = await self.get(guild_mentions_db_key)
        return rolesToMention.decode("UTF-8")

    async def delete_guild_mentions(self, guild_id):
        """Deletes all mentions for the given guild_id
        Returns the number of keys that were deleted
        """
        guild_mentions_db_key = f"slb.{str(guild_id)}"
        return await redis.delete(guild_mentions_db_key)


# This is the instance that will be imported and used by all other files
redis = RedisClient(REDIS_HOST, REDIS_PORT, REDIS_DB)
