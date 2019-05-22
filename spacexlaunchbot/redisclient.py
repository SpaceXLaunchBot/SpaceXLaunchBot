"""Redis Structure
All keys are prepended with "slb:"
Variables in the keys described below are enclosed in (brackets)

Key                       | Value
--------------------------|-------------------------------------------------------------
subscribed_channels       | A Redis SET of channel IDs that are to be sent notifications
guild:(guild_id)          | A hash containing options for that guild. This includes:
                          | "mentions": String of channels, users, etc. to ping for a launch
metric:(metric_name)      | Currently not used. Example use: slb:metric:commands_used
notification_task_store   | A Redis hash containing variables that need to persist
                          | between runs of the notification task. This includes:
                          | "ls_notif_sent": "True" OR "False" (str not bool)
                          | "li_embed_dict": pickled(embed_dict)
                          | See bgtasks.notification_task to see how each var is used
"""

import logging, pickle, aredis
import statics, config


class RedisClient(aredis.StrictRedis):
    def __init__(self, host, port, db_num):
        super().__init__(host=host, port=port, db=db_num)
        logging.info(f"Connected to Redis at {host}:{port} on DB {db_num}")

    async def init_defaults(self):
        """If the database is new, create default values for needed keys
        """
        if not await self.exists("slb:notification_task_store"):
            logging.info("slb:notification_task_store does not exist, creating")
            await self.set_notification_task_store("False", statics.general_error_embed)

    async def get_notification_task_store(self):
        """Gets and decodes / deserializes variables from notification_task_store
        Returns a tuple with these indexes:
        0: ls_notif_sent
        1: li_embed_dict
        """
        hash_key = "slb:notification_task_store"

        ls_notif_sent = await self.hget(hash_key, "ls_notif_sent")
        li_embed_dict = await self.hget(hash_key, "li_embed_dict")

        return (ls_notif_sent.decode("UTF-8"), pickle.loads(li_embed_dict))

    async def set_notification_task_store(self, ls_notif_sent, li_embed_dict):
        """Update / create the hash for notification_task_store
        Automatically encodes / serializes both arguments
        """
        hash_key = "slb:notification_task_store"

        ls_notif_sent = ls_notif_sent.encode("UTF-8")
        li_embed_dict = pickle.dumps(li_embed_dict, protocol=pickle.HIGHEST_PROTOCOL)

        await self.hset(hash_key, "ls_notif_sent", ls_notif_sent)
        await self.hset(hash_key, "li_embed_dict", li_embed_dict)

    async def set_guild_mentions(self, guild_id, to_mention):
        """Set mentions for a guild
        guild_id can be int or str
        to_mention should be an string of roles / tags / etc.
        """
        guild_key = f"slb:guild:{str(guild_id)}"
        to_mention = to_mention.encode("UTF-8")
        await self.hset(guild_key, "mentions", to_mention)

    async def get_guild_mentions(self, guild_id):
        """Returns a string of mentions for that guild
        guild_id can be int or str
        returns False if guild_id does not have any settings stored
        """
        guild_key = f"slb:guild:{str(guild_id)}"
        to_mention = await self.hget(guild_key, "mentions")
        if not to_mention:
            return False
        return to_mention.decode("UTF-8")

    async def delete_guild_mentions(self, guild_id):
        """Deletes all mentions for the given guild_id
        guild_id can be int or str
        Returns the number of keys that were deleted
        """
        guild_key = f"slb:guild:{str(guild_id)}"
        return await redis.hdel(guild_key, "mentions")


# This is the instance that will be imported and used by all other files
redis = RedisClient(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)
