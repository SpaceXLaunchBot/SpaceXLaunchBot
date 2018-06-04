"""
Async Redis stuff

Redis structure:

Key                       | Value
--------------------------|-----------------------------------------------------
subscribedChannels        | string: pickled( subscribedChannelList )
launchNotifSent           | string: true / false
latestLaunchInfoEmbedDict | string: pickled( launchInfoEmbedDict )
"""

from aredis import StrictRedis
import pickle

class redisClient(object):
    def __init__(socketPath):
        self.r = StrictRedis(unix_socket_path=socketPath)

    async def get(key, obj=False):
        if obj:
            # Return an un-serialized object
            return pickle.loads(await self.r.get(key))
        return await self.r.get(key)

    async def set(key, value):
        # Currently accepts strings or objects (includes lists)
        if isinstance(value, str):
            return await self.r.get(key)
        # Set an object by serializing
        value = pickle.dumps(value)
        return await self.r.set(key, value)

def startRedisConnection():
    # Global so it can be imported after being instanced
    global redisConn
    redisConn = redisClient("/tmp/redis.sock")
    return redisConn
