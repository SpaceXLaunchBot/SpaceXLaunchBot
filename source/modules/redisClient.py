"""
Redis structure
---------------
All keys are prepended with "slb."

Key                   | Value
----------------------|-----------------------------------------------------------------
subscribedChannels    | A Redis SET of channel IDs that are to be sent notifications
str(Guild ID)         | A string containing Discord mentions (channels, users, etc.)
metrics               | A Redis hash containing these fields:
                      | "totalCommands" - The total number of commands issued
notificationTaskStore | A Redis hash containing variables that need to persist between
                      | runs of the notification background task(s). This includes:
                      | "launchingSoonNotifSent" = "True" OR "False" (str not bool)
                      | "latestLaunchInfoEmbedDict" = pickled(launchInfoEmbedDict)
"""

from aredis import StrictRedis
import logging
import pickle

from modules.statics import generalErrorEmbed

logger = logging.getLogger(__name__)


class redisClient(StrictRedis):
    def __init__(self, host="127.0.0.1", port=6379, dbNum=0):
        super().__init__(host=host, port=port, db=dbNum)
        logger.info(f"Connected to Redis at {host}:{port} on DB {dbNum}")

    async def initDefaults(self):
        """
        If database is new, create default values for needed keys
        """
        if not await self.exists("slb.notificationTaskStore"):
            logger.debug("slb.notificationTaskStore hash does not exist, creating")
            await self.setNotificationTaskStore("False", generalErrorEmbed)

    async def getNotificationTaskStore(self):
        """
        Gets and decodes variables from notificationTaskStore
        """
        launchingSoonNotifSent = await self.hget(
            "slb.notificationTaskStore", "launchingSoonNotifSent"
        )
        latestLaunchInfoEmbedDict = await self.hget(
            "slb.notificationTaskStore", "latestLaunchInfoEmbedDict"
        )
        return {
            "launchingSoonNotifSent": launchingSoonNotifSent.decode("UTF-8"),
            "latestLaunchInfoEmbedDict": pickle.loads(latestLaunchInfoEmbedDict),
        }

    async def setNotificationTaskStore(
        self, launchingSoonNotifSent, latestLaunchInfoEmbedDict
    ):
        """
        Update / create the hash for notificationTaskStore
        Automatically encodes both arguments
        """
        launchingSoonNotifSent = launchingSoonNotifSent.encode("UTF-8")
        latestLaunchInfoEmbedDict = pickle.dumps(
            latestLaunchInfoEmbedDict, protocol=pickle.HIGHEST_PROTOCOL
        )
        await self.hset(
            "slb.notificationTaskStore",
            "launchingSoonNotifSent",
            launchingSoonNotifSent,
        )
        await self.hset(
            "slb.notificationTaskStore",
            "latestLaunchInfoEmbedDict",
            latestLaunchInfoEmbedDict,
        )

    async def setGuildMentions(self, guildID, rolesToMention):
        """
        Set mentions for a guild
        guildID can be int or str
        rolesToMention should be an string of roles / tags / etc.
        """
        guildMentionsDBKey = f"slb.{str(guildID)}"
        rolesToMention = rolesToMention.encode("UTF-8")
        await self.set(guildMentionsDBKey, rolesToMention)

    async def getGuildMentions(self, guildID):
        """
        Returns a string of mentions for that guild
        guildID can be int or str
        returns False if guildID does not have any settings stored
        """
        guildMentionsDBKey = f"slb.{str(guildID)}"
        if not await self.exists(guildMentionsDBKey):
            return False
        rolesToMention = await self.get(guildMentionsDBKey)
        return rolesToMention.decode("UTF-8")


"""
When this is imported for the first time, set up our Redis connection and save
to a variable so anything importing this can access it
"""
redisConn = redisClient()
