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

logger = logging.getLogger(__name__)

class redisClient(object):
    def __init__(self, socketPath):
        self.r = StrictRedis(unix_socket_path=socketPath)

    async def get(self, key, obj=False):
        try:
            if obj:
                # Return an un-serialized object
                return pickle.loads(await self.r.get(key))
            return await self.r.get(key)
        except Exception as e:
            logger.error(f"Failed to get data from Redis: {type(e).__name__}: {e}")
            return 0

    async def set(self, key, value):
        try:
            # Currently accepts strings or objects (includes lists)
            if isinstance(value, str):
                return await self.r.set(key)
            # Set an object by serializing
            value = pickle.dumps(value)
            return await self.r.set(key, value)
        except Exception as e:
            logger.error(f"Failed to set data in Redis: {type(e).__name__}: {e}")
            return 0

def startRedisConnection():
    # Global so it can be imported after being set to a redisClient instance
    global redisConn
    redisConn = redisClient("/tmp/redis.sock")
    return redisConn
