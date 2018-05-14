"""
Handles interactions with the discordbots.org API
"""

from asyncio import sleep
from os import environ
import aiohttp
import utils

try:
    dblToken = environ["dblToken"]
except KeyError:
    utils.err("Environment Variable \"dblToken\" cannot be found")
dblHeaders = {"Authorization": dblToken, "Content-Type": "application/json"}

class dblClient(object):
    def __init__(self, discordClient):
        self.discordClient = discordClient
        self.dblURL = "https://discordbots.org/api/bots/{}/stats".format(discordClient.user.id)

    async def updateServerCount(self, serverCount):
        async with aiohttp.ClientSession() as session:
                try:
                    await session.post(self.dblURL, json={"server_count": serverCount}, headers=dblHeaders)
                except Exception as e:
                    print("[updateServerCount] Failed to post server count:\n{}: {}".format(type(e).__name__, e))
