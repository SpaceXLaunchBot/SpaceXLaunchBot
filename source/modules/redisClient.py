"""
Async Redis stuff

Redis structure:

Key                       | Value
--------------------------|------------------------------------------
subscribedChannels        | string: pickled( subscribedChannelList )
launchNotifSent           | string: true / false
latestLaunchInfoEmbedDict | string: pickled( launchInfoEmbedDict )
"""

from aredis import StrictRedis
import logging
import pickle

from modules import errors

logger = logging.getLogger(__name__)

class redisClient(StrictRedis):
    def __init__(self, unix_socket_path):
        super().__init__(unix_socket_path=unix_socket_path)
        logger.info(f"Connected to {unix_socket_path}")

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
        channels = await self.safeGet("subscribedChannels")
        if channels:
            return pickle.loads(channels)
        return []  # Cannot get any subscribed channels so return empty
    
    async def getLaunchNotifSent(self):
        lns = await self.safeGet("launchNotifSent")
        if lns:
            return lns
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
