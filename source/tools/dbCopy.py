"""
Copies db 0 to db 1
"""

import asyncio
from aredis import StrictRedis

async def doRedisStuff():
    print("Connecting to /tmp/redis.sock")
    redisConn0 = StrictRedis(unix_socket_path="/tmp/redis.sock", db=0)
    redisConn1 = StrictRedis(unix_socket_path="/tmp/redis.sock", db=1)
    
    print("Setting values")
    await redisConn1.set("subscribedChannels", await redisConn0.get("subscribedChannels"))
    await redisConn1.set("launchNotifSent", await redisConn0.get("launchNotifSent"))
    await redisConn1.set("latestLaunchInfoEmbedDict", await redisConn0.get("latestLaunchInfoEmbedDict"))
    
    print("Done")

loop = asyncio.get_event_loop()
loop.run_until_complete(doRedisStuff())
