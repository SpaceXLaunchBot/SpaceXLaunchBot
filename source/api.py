"""
api.py

Contains the stuff for dealing with the r/SpaceX API
"""

from discord import Embed
import aiohttp

hexColours = {"errorRed": 0xFF0000, "falconRed": 0xEE0F46}
upcomingLaunchesURL = "https://api.spacexdata.com/v2/launches/upcoming?order=asc"

# Embeds to send if an error happens
APIErrorEmbed = Embed(title="Error", description="An API error occurred, contact @Dragon#0571", color=hexColours["errorRed"])
generalErrorEmbed = Embed(title="Error", description="An error occurred, contact @Dragon#0571", color=hexColours["errorRed"])

async def getNextLaunchJSON():
    """
    Using aiohttp, grab the latest launch info
    Returns 0 if fail
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(upcomingLaunchesURL) as response:
            if response.status != 200:
                return 0
            return list(await response.json())[0]
