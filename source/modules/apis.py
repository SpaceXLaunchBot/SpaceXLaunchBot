import aiohttp
import logging

logger = logging.getLogger(__name__)


class spacexApi(object):
    """
    Handles interactions with the SpaceX API
    Ratelimit is (as of 13/01/19) 50 req/sec per IP address, which should be fine
    """

    @staticmethod
    async def getNextLaunchJSON(debug=False):
        """
        Using aiohttp, grab the latest launch info
        Returns -1 if fail
        """

        route = "next"
        if debug:
            route = "latest"

        upcomingLaunchesURL = f"https://api.spacexdata.com/v3/launches/{route}"

        async with aiohttp.ClientSession() as session:
            async with session.get(upcomingLaunchesURL) as response:
                if response.status != 200:
                    logger.error(
                        "Failed to get data from SpaceX API: response.status != 200"
                    )
                    return -1
                try:
                    return await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    logger.error(
                        "Failed to get data from SpaceX API: JSON decode failed"
                    )
                    return -1


class dblApi(object):
    """
    Handles interactions with the discordbots.org API
    """

    def __init__(self, discordClient, dblToken):
        self.dblURL = f"https://discordbots.org/api/bots/{discordClient.user.id}/stats"
        self.headers = {"Authorization": dblToken, "Content-Type": "application/json"}

    async def updateGuildCount(self, guildCount):
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(
                    self.dblURL, json={"server_count": guildCount}, headers=self.headers
                )
            except Exception as e:
                logger.error(f"Failed to post guild count: {type(e).__name__}: {e}")
