import aiohttp
import logging

logger = logging.getLogger(__name__)

class spacexAPI(object):
    """
    Handles interactions with the SpaceX API
    """
    
    @staticmethod
    async def getNextLaunchJSON():
        """
        Using aiohttp, grab the latest launch info
        Returns -1 if fail
        """
        upcomingLaunchesURL = "https://api.spacexdata.com/v2/launches/next"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(upcomingLaunchesURL) as response:
                    if response.status != 200:
                        logger.error("Failed to get data from SpaceX API: response.status != 200")
                        return -1
                    return await response.json()
            except Exception as e:
                logger.error(f"Failed to get data from SpaceX API: {type(e).__name__}: {e}")
                return -1

class dblApiClient(object):
    """
    Handles interactions with the discordbots.org API
    """

    def __init__(self, discordClient, dblToken):
        self.dblURL = f"https://discordbots.org/api/bots/{discordClient.user.id}/stats"
        self.headers = {"Authorization": dblToken, "Content-Type": "application/json"}

    async def updateGuildCount(self, guildCount):
        async with aiohttp.ClientSession() as session:
                try:
                    await session.post(self.dblURL, json={"server_count": guildCount}, headers=self.headers)
                except Exception as e:
                    logger.error(f"Failed to post guild count: {type(e).__name__}: {e}")
