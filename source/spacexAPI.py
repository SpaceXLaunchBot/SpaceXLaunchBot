"""
Contains the stuff for dealing with the r/SpaceX API
"""

import aiohttp

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
                    return 0
                return (await response.json())[0]
        except Exception as e:
            print("[getNextLaunchJSON] Failed to get data from SpaceX API:\n{}: {}".format(type(e).__name__, e))
            return 0
