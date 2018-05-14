"""
api.py

Contains the stuff for dealing with the r/SpaceX API
"""

from discord import Embed
import aiohttp

hexColours = {"errorRed": 0xFF0000, "falconRed": 0xEE0F46}
upcomingLaunchesURL = "https://api.spacexdata.com/v2/launches/upcoming?order=asc"

# Embeds to send if an error happens
apiErrorEmbed = Embed(title="Error", description="An API error occurred, contact @Dragon#0571", color=hexColours["errorRed"])
generalErrorEmbed = Embed(title="Error", description="An error occurred, contact @Dragon#0571", color=hexColours["errorRed"])

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
