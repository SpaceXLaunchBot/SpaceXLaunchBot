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

def startRedisConnection():
    global redisConn
    redisConn = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")
    return redisConn
