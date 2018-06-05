"""
Deconstructs data.pkl into Python vars then pushes them to the Redis server
Expects the data.pkl file to be in the same directory as this script
"""

import pickle
import asyncio
from aredis import StrictRedis

with open("data.pkl", "rb") as f:
    localData = pickle.load(f)
    print("data.pkl loaded")

async def doRedisStuff():
    print("Connecting to /tmp/redis.sock")
    client = StrictRedis(unix_socket_path="/tmp/redis.sock")
    print("Connected, flushing db")
    await client.flushdb()
    print("Setting values")
    await redisConn.set("subscribedChannels", localData["subscribedChannels"])
    await redisConn.set("launchNotifSent", localData["launchNotifSent"])
    await redisConn.set("latestLaunchInfoEmbedDict", localData["latestLaunchInfoEmbedDict"])
    print("Done")

loop = asyncio.get_event_loop()
loop.run_until_complete(doRedisStuff())
