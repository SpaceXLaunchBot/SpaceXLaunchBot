"""
Changes "launchNotifSent" Redis key value from a list of strings to a list
of integers
"""

import asyncio
from aredis import StrictRedis
import pickle

async def doRedisStuff():
    print("Connecting to /tmp/redis.sock")
    r = StrictRedis(unix_socket_path="/tmp/redis.sock", db=0)
    
    print("Getting subscribedChannels")
    idList = pickle.loads(await r.get("subscribedChannels"))
    newList = []

    print(idList)
    
    for x in idList:
        newList.append(int(x))
        print("Processed", x)
    
    print("setting in Redis")

    await r.set("subscribedChannels", pickle.dumps(newList))  

    print(newList)
    print("now of type:", type(newList[0]))

    print("Done")

loop = asyncio.get_event_loop()
loop.run_until_complete(doRedisStuff())
