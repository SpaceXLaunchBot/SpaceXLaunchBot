"""
Handles interactions with the discordbots.org API
"""

from os import environ
import asyncio
import utils
import dbl

try:
    dblToken = environ["dblToken"]
except KeyError:
    utils.err("Environment Variable \"dblToken\" cannot be found")

def dblBackgroundTask(clientObject):
    dblpy = dbl.Client(clientObject, dblToken)
    while 1:
        try:
            await dblpy.post_server_count()
        except Exception as e:
            print("[dbl] Failed to post server count\n{}: {}".format(type(e).__name__, e))
        await asyncio.sleep(1800)
