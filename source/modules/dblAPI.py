"""
Handles interactions with the discordbots.org API
"""

from asyncio import sleep
from os import environ
import aiohttp
import logging

from modules.utils import loadEnvVar

logger = logging.getLogger(__name__)

dblToken = loadEnvVar("dblToken")
dblHeaders = {"Authorization": dblToken, "Content-Type": "application/json"}

class dblClient(object):
    def __init__(self, discordClient):
        self.dblURL = f"https://discordbots.org/api/bots/{discordClient.user.id}/stats"

    async def updateGuildCount(self, guildCount):
        async with aiohttp.ClientSession() as session:
                try:
                    await session.post(self.dblURL, json={"server_count": guildCount}, headers=dblHeaders)
                except Exception as e:
                    logger.error(f"Failed to post guild count: {type(e).__name__}: {e}")
