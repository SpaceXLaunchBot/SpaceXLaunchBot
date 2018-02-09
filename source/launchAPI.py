from discord import Embed
import asyncio
import aiohttp
from datetime import datetime

upcomingLaunchesURL = "https://api.spacexdata.com/v2/launches/upcoming?order=asc"
rocketImages = {
    "F9": "",
    "FH": "",
    "DR": ""
}

async def getNextLaunchEmbed(plus=False):
    async with aiohttp.ClientSession() as session:
        async with session.get(upcomingLaunchesURL) as response:
            nextLaunch = list(await response.json())[0]
    embed = Embed(
        title="title",
        description="description",
        footer="footer",
        url="",
        color=0x00ff00
    )
    return embed
