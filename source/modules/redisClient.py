"""
Redis structure:
Key                       | Value
--------------------------|-----------------------------------------------------
subscribedChannels        | pickled( subscribedChannelList )
launchNotifSent           | "True" / "False" (str not bool)
latestLaunchInfoEmbedDict | pickled( launchInfoEmbedDict )
Guild snowflake as a str  | Mentions to ping when a "launching soon" msg is sent

Planned new Redis structure:
Key                       | Value
--------------------------|-----------------------------------------------------
Guild snowflake           | pickled ( A dictionary containing server options )
                          | Also use this to replace subscribedChannels, read
                          | the warning https://redis.io/commands/keys here and
                          | decide how to use (or maybe use sets?)
launchingSoonNotifSent    | "True" / "False" (str not bool)
latestLaunchInfoEmbedDict | pickled( launchInfoEmbedDict )
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

    async def safeGet(self, key, deserialize=False):
        """
        Returns 0 if get(key) fails or a value does not exist for that key
        If deserialize is False, the returned value is decoded using UTF-8
        """
        try:
            value = await self.get(key)
            if not value:
                return 0
            elif deserialize:
                return pickle.loads(value)
            else:
                return value.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to safeGet data from Redis: key: {key} error: {type(e).__name__}: {e}")
            return 0

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
            logger.error(f"Failed to safeSet data in Redis: key: {key} error: {type(e).__name__}: {e}")
            return 0
    
    async def getSubscribedChannelIDs(self):
        """
        Returns a dict: {"list": list, "err": True/False}
        This is so we can return & iterate a list even if there is an error,
        which means in methods where it doesen't matter if there was an error or
        not, we can just ignore it and iterate an empty list instead of having
        to check for an error. e.g. the reaper doesen't care if there was an err
        """
        channels = await self.safeGet("subscribedChannels", deserialize="True")
        if channels or channels == []:
            # An empty list isn't an err
            return {"list": channels, "err": False}
        # Cannot get any subscribed channels so return empty
        return {"list": [], "err": True}
    
    async def getLaunchNotifSent(self):
        lns = await self.safeGet("launchNotifSent")
        if lns:
            return lns
        return "False"
    
    async def getLatestLaunchInfoEmbedDict(self):
        llied = await self.safeGet("latestLaunchInfoEmbedDict", deserialize="True")
        if llied:
            return llied
        return 0

"""
When this is imported for the first time, set up our Redis connection and save
to a variable so anything importing this can access it
"""
redisConn = redisClient()
