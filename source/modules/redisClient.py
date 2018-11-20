"""
Redis structure:
Key                       | Value
--------------------------|-----------------------------------------------------
subscribedChannels        | A Redis SET of channel IDs that are subscribed to the
                          | notification service
str( Guild snowflake )    | A Redis hash containing server options
notificationTaskStore     | A Redis hash containing variables that need to
                          | persist between runs of the notification background
                          | task. This currently includes:
                          | "launchingSoonNotifSent" = "True" OR "False" (str not bool)
                          | "latestLaunchInfoEmbedDict" = pickled ( launchInfoEmbedDict )
metricsStore              | Used for bot metrics, currently unused & unsure of structure
"""

from aredis import StrictRedis
import logging
import pickle

logger = logging.getLogger(__name__)

class redisClient(StrictRedis):
    def __init__(self, host="127.0.0.1", port=6379, dbNum=0):
        # Uses redis default host, port, and dbnum by default
        super().__init__(host=host, port=port, db=dbNum)
        logger.info(f"Connected to {host}:{port} on db num {dbNum}")

    async def safeSadd(self, key, value):
        """
        Returns -1 if sadd fails
        value is encoded using UTF-8 if it is a string
        """
        try:
            if type(value) == str:
                return await self.sadd(key, value.encode("UTF-8"))
            return await self.sadd(key, value)
        except Exception as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            return -1

    async def safeGet(self, key, deserialize=False):
        """
        Returns -1 if get(key) fails or a value does not exist for that key
        If deserialize is False, the returned value is decoded using UTF-8
        """
        try:
            value = await self.get(key)
            if not value:
                return -1
            elif deserialize:
                return pickle.loads(value)
            else:
                return value.decode("UTF-8")
        except Exception as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            return -1

    async def safeSet(self, key, value, serialize=False):
        """
        Returns 0 if set() fails
        If serialize is False, the set value is encoded using UTF-8
        """
        try:
            if serialize:
                return await self.set(key, pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))    
            return await self.set(key, value.encode("UTF-8"))
        except Exception as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            return -1

    async def getNotificationTaskStore(self):
        """
        Gets variables from notificationTaskStore
        Automatically decodes variables
        """
        launchingSoonNotifSent = (await self.hget("notificationTaskStore", "launchingSoonNotifSent")).decode("UTF-8")
        latestLaunchInfoEmbedDict = pickle.loads(await self.hget("notificationTaskStore", "latestLaunchInfoEmbedDict"))
        return {
            "launchingSoonNotifSent": launchingSoonNotifSent,
            "latestLaunchInfoEmbedDict": latestLaunchInfoEmbedDict
        }

    async def setNotificationTaskStore(self, launchingSoonNotifSent, latestLaunchInfoEmbedDict):
        """
        Update / create the hash for notificationTaskStore
        Automatically encodes both arguments
        Returns 1 if successful, -1 if error
        """
        launchingSoonNotifSent = launchingSoonNotifSent.encode("UTF-8")
        latestLaunchInfoEmbedDict = pickle.dumps(latestLaunchInfoEmbedDict, protocol=pickle.HIGHEST_PROTOCOL)
        try:
            await self.hset("notificationTaskStore", "launchingSoonNotifSent", launchingSoonNotifSent)
            await self.hset("notificationTaskStore", "latestLaunchInfoEmbedDict", latestLaunchInfoEmbedDict)
        except Exception as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            return -1
        return 1

    async def setGuildSettings(self, guildID, rolesToMention):
        """
        Saves a guilds settings using a Redis hash
        guildID can be int or str
        rolesToMention should be an array of roles / tags / etc. OR None
        returns -1 on error
        """
        guildID = str(guildID)  # Make sure we are using a string
        try:            
            rolesToMentionPickled = pickle.dumps(rolesToMention, protocol=pickle.HIGHEST_PROTOCOL)
            await self.hset(guildID, "rolesToMention", rolesToMentionPickled)
            return 0
        except Exception as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            return -1

    async def getGuildSettings(self, guildID):
        """
        Returns a guilds settings from Redis
        guildID can be int or str
        returns a dict of varName : var
        returns -1 on error
        returns 0 if guildID does not have any settings set
        """
        guildID = str(guildID)

        if not await self.exists(guildID):
            return 0

        # Wrap Redis operations in error catching block
        try:
            rolesToMentionPickled = await self.hget(guildID, "rolesToMention")
        except Exception as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            return -1
        
        rolesToMention = pickle.loads(rolesToMentionPickled)
        return {
            "rolesToMention": rolesToMention
        }

"""
When this is imported for the first time, set up our Redis connection and save
to a variable so anything importing this can access it
"""
redisConn = redisClient()
