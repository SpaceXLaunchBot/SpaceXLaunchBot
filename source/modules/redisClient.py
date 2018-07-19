"""
Async Redis stuff

Redis structure:

Key                       | Value
--------------------------|------------------------------------------
subscribedChannels        | pickled( subscribedChannelList )
launchNotifSent           | True / False as a string
latestLaunchInfoEmbedDict | pickled( launchInfoEmbedDict )
nextlaunchRequestCount    | number
"""

# TODO: Explicitly encode / decode - https://stackoverflow.com/a/25745079

from aredis import StrictRedis
import logging
import pickle

from modules import errors

logger = logging.getLogger(__name__)

class redisClient(StrictRedis):
    def __init__(self, unix_socket_path, dbNum=0):
        super().__init__(unix_socket_path=unix_socket_path, db=dbNum)
        logger.info(f"Connected to {unix_socket_path} on db num {dbNum}")

    async def safeGet(self, key):
        try:
            return await self.get(key)
        except Exception as e:
            logger.error(f"Failed to safeGet data from Redis: {type(e).__name__}: {e}")
            return 0

    async def safeSet(self, key, value, serialize=False):
        try:
            if serialize:
                return await self.set(key, pickle.dumps(value))    
            return await self.set(key, value)
        except Exception as e:
            logger.error(f"Failed to safeSet data in Redis: {type(e).__name__}: {e}")
            return 0
    
    async def getSubscribedChannelIDs(self):
        """
        Returns a dict: {"list": list, "err": True/False}
        This is so we can return & iterate a list even if there is an error,
        which means in methods where it doesen't matter if there was an error or
        not, we can just ignore it and iterate an empty list instead of having
        to check for an error. e.g. the reaper doesen't care if there was an err
        """
        channels = await self.safeGet("subscribedChannels")
        if channels:
            return {"list": pickle.loads(channels), "err": False}
        # Cannot get any subscribed channels so return empty
        return {"list": [], "err": True}
    
    async def getLaunchNotifSent(self):
        lns = await self.safeGet("launchNotifSent")
        if lns:
            # get returns a byteString
            return lns.decode("UTF-8")
        return "False"
    
    async def getLatestLaunchInfoEmbedDict(self):
        llied = await self.safeGet("latestLaunchInfoEmbedDict")
        if llied:
            return pickle.loads(llied)
        return 0

def startRedisConnection():
    # Global so it can be imported after being set to a redisClient instance
    global redisConn
    redisConn = redisClient("/tmp/redis.sock")
    return redisConn
