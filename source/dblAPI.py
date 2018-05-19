"""
Handles interactions with the discordbots.org API
"""

from asyncio import sleep
from os import environ
import aiohttp
import logging

from utils import loadEnvVar

logger = logging.getLogger(__name__)

dblToken = loadEnvVar("dblToken")
dblHeaders = {"Authorization": dblToken, "Content-Type": "application/json"}

class dblClient(object):
    def __init__(self, discordClient):
        self.dblURL = "https://discordbots.org/api/bots/{}/stats".format(discordClient.user.id)

    async def updateServerCount(self, serverCount):
        async with aiohttp.ClientSession() as session:
                try:
                    await session.post(self.dblURL, json={"server_count": serverCount}, headers=dblHeaders)
                except Exception as e:
                    logger.error("Failed to post server count: {}: {}".format(type(e).__name__, e))
