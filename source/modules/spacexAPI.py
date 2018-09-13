"""
Contains the stuff for dealing with the r/SpaceX API
"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

upcomingLaunchesURL = "https://api.spacexdata.com/v2/launches/upcoming?order=asc"

async def getNextLaunchJSON():
    """
    Using aiohttp, grab the latest launch info
    Returns 0 if fail
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(upcomingLaunchesURL) as response:
                if response.status != 200:
                    logger.error("Failed to get data from SpaceX API: response.status != 200")
                    return 0
                return (await response.json())[0]
        except Exception as e:
            logger.error(f"Failed to get data from SpaceX API: {type(e).__name__}: {e}")
            return 0
