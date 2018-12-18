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

from modules.statics import generalErrorEmbed

logger = logging.getLogger(__name__)

class redisClient(StrictRedis):
    def __init__(self, host="127.0.0.1", port=6379, dbNum=0):
        # Uses redis default host, port, and dbnum by default
        super().__init__(host=host, port=port, db=dbNum)
        logger.info(f"Connected to {host}:{port} on db num {dbNum}")

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
        """
        launchingSoonNotifSent = launchingSoonNotifSent.encode("UTF-8")
        latestLaunchInfoEmbedDict = pickle.dumps(latestLaunchInfoEmbedDict, protocol=pickle.HIGHEST_PROTOCOL)
        await self.hset("notificationTaskStore", "launchingSoonNotifSent", launchingSoonNotifSent)
        await self.hset("notificationTaskStore", "latestLaunchInfoEmbedDict", latestLaunchInfoEmbedDict)

    async def setGuildSettings(self, guildID, rolesToMention):
        """
        Saves a guilds settings using a Redis hash
        guildID can be int or str
        rolesToMention should be an string of roles / tags / etc. OR None
        """
        guildID = str(guildID)  # Make sure we are using a string
        if rolesToMention:
            await self.hset(guildID, "rolesToMention", rolesToMention)

    async def getGuildSettings(self, guildID):
        """
        Returns a guilds settings from Redis
        guildID can be int or str
        returns a dict of varName : var
        returns 0 if guildID does not have any settings stored
        """
        guildID = str(guildID)
        if not await self.exists(guildID):
            return 0
        rolesToMention = await self.hget(guildID, "rolesToMention")
        return {
            "rolesToMention": rolesToMention
        }

"""
When this is imported for the first time, set up our Redis connection and save
to a variable so anything importing this can access it
"""
redisConn = redisClient()
