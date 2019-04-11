import aiohttp
import logging

logger = logging.getLogger(__name__)


class spacexApi:
    """
    Handles interactions with the SpaceX API
    As of 13/01/19, API ratelimit is 50 req/sec per IP
    """

    @staticmethod
    async def getNextLaunchJSON(previous=False):
        """
        Using aiohttp, get the latest launch info in JSON format
        If previous=True, use data from previous launch (for debugging)
        Returns -1 on failure
        """

        if previous:
            route = "latest"
        else:
            route = "next"

        upcomingLaunchesURL = f"https://api.spacexdata.com/v3/launches/{route}"

        async with aiohttp.ClientSession() as session:
            async with session.get(upcomingLaunchesURL) as response:
                if response.status == 200:
                    try:
                        nextLaunchJSON = await response.json()
                    except aiohttp.client_exceptions.ContentTypeError:
                        logger.error("SpaceX API: JSON decode failed")
                        return -1
                else:
                    logger.error(f"SpaceX API: Response status: {response.status}")
                    return -1
                return nextLaunchJSON


class dblApi:
    """
    Handles interactions with the discordbots.org API
    """

    def __init__(self, clientID, dblToken):
        self.dblURL = f"https://discordbots.org/api/bots/{clientID}/stats"
        self.headers = {"Authorization": dblToken, "Content-Type": "application/json"}

    async def updateGuildCount(self, guildCount):
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.dblURL, json={"server_count": guildCount}, headers=self.headers
            )
