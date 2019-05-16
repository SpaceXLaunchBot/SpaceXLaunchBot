import aiohttp
import logging

logger = logging.getLogger(__name__)


class SpacexApi:
    """Handles interactions with the SpaceX API
    As of 13/01/19, API ratelimit is 50 req/sec per IP
    """

    @staticmethod
    async def get_next_launch_dict(previous=False):
        """Using aiohttp, get the latest launch info
        If previous=True, use data from previous launch (for debugging)
        Returns -1 on failure
        """

        if previous:
            route = "latest"
        else:
            route = "next"

        upcoming_launches_url = f"https://api.spacexdata.com/v3/launches/{route}"

        async with aiohttp.ClientSession() as session:
            async with session.get(upcoming_launches_url) as response:
                if response.status == 200:
                    try:
                        next_launch_dict = await response.json()
                    except aiohttp.client_exceptions.ContentTypeError:
                        logger.error("SpaceX API: JSON decode failed")
                        return -1
                else:
                    logger.error(f"SpaceX API: Response status: {response.status}")
                    return -1
                return next_launch_dict


class DblApi:
    """Handles interactions with the discordbots.org API
    """

    def __init__(self, client_id, dbl_token):
        self.dblURL = f"https://discordbots.org/api/bots/{client_id}/stats"
        self.headers = {"Authorization": dbl_token, "Content-Type": "application/json"}

    async def update_guild_count(self, guild_count):
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.dblURL, json={"server_count": guild_count}, headers=self.headers
            )
