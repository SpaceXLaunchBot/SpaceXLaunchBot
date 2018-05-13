"""
Handles interactions with the discordbots.org API
"""

from os import environ
import asyncio
import aiohttp
import utils

dblAPI = "https://discordbots.org/api/bots/{}/stats"

try:
    dblToken = environ["dblToken"]
except KeyError:
    utils.err("Environment Variable \"dblToken\" cannot be found")

dblHeaders = {"Authorization": dblToken, "Content-Type": "application/json"}

async def dblBackgroundTask(clientObject):

    await clientObject.wait_until_ready()
    dblUpdateURL = dblAPI.format(clientObject.user.id)

    while not client.is_closed:
        # POST Stats
        serverCount = len(list(clientObject.servers))

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(dblUpdateURL, json={"server_count": serverCount}, headers=dblHeaders)
        except Exception as e:
            print("[dbl] Failed to post server count\n{}: {}".format(type(e).__name__, e))

        await asyncio.sleep(1800)
