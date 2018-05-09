"""
api.py

Contains functions for dealing with the r/SpaceX API
"""

from utils import getUTCFromTimestamp
from copy import deepcopy
from discord import Embed
import asyncio
import aiohttp

rocketIDImages = {
    "falcon9": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/falcon9.png",
    "falconheavy": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/falconHeavy.png",
    "falcon1": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/logo.jpg"
}
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

async def getLaunchInfoEmbed(nextLaunchJSON):
    # No need to do the same thing twice
    launchEmbed = await getLaunchInfoEmbedLite(nextLaunchJSON, small=False)

    # Don't just copy a pointer, copy the whole thing into another section of memory
    originalLaunchEmbedLite = deepcopy(launchEmbed)
    
    # Update with longer description
    launchEmbed.description = "A {} rocket carrying {} payload(s), launching from {}".format(
        nextLaunchJSON["rocket"]["rocket_name"],
        len(nextLaunchJSON["rocket"]["second_stage"]["payloads"]),
        nextLaunchJSON["launch_site"]["site_name_long"]
    )

    # Add a field showing each reused component
    reusing = []
    for component in nextLaunchJSON["reuse"]:
        if nextLaunchJSON["reuse"][component]:
            reusing.append(component)
    launchEmbed.add_field(name="Reused components:", value=", ".join(reusing))

    # Add a field for each payload, with basic information
    for payload in nextLaunchJSON["rocket"]["second_stage"]["payloads"]:
        launchEmbed.add_field(
            name="Payload: {}".format(payload["payload_id"]),
            value="Type: {}\nOrbit: {}\nMass: {}kg\nCustomer(s): {}".format(
                payload["payload_type"],
                payload["orbit"],
                payload["payload_mass_kg"],
                ", ".join(payload["customers"])
            )
        )

    return launchEmbed, originalLaunchEmbedLite

async def getLaunchInfoEmbedLite(nextLaunchJSON, small=True):
    # A "lite" version of the embed that should never reach the embed size limit
    # small is used to determine whether this is going to be used to make the bigger embed,
    # or actually needs to contain less content

    launchEmbed = Embed(
        title="r/SpaceX Discussion",
        url = nextLaunchJSON["links"]["reddit_campaign"],
        description="This information has been reduced as the data is too large to contain in this embed",
        color=hexColours["falconRed"]
    )

    # Set thumbnail depending on rocket ID
    launchEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])
    launchEmbed.set_author(name="Launch #{}".format(nextLaunchJSON["flight_number"]))

    # Actually making a lite embed, so add reduced info here
    if small:
        # Info in new field
        launchEmbed.add_field(name="Information", value="A {} rocket carrying {} payload(s), launching from {}".format(
            nextLaunchJSON["rocket"]["rocket_name"],
            len(nextLaunchJSON["rocket"]["second_stage"]["payloads"]),
            nextLaunchJSON["launch_site"]["site_name_long"]
        ))

    # Add a field for the launch date  
    UTCDate = await getUTCFromTimestamp(nextLaunchJSON["launch_date_unix"])
    launchEmbed.add_field(name="Launch date", value=UTCDate)

    return launchEmbed

async def getLaunchNotifEmbed(nextLaunchJSON):
    notifEmbed = Embed(
        title="r/SpaceX Discussion",
        url = nextLaunchJSON["links"]["reddit_campaign"],
        description="{} is launching soon!".format(nextLaunchJSON["mission_name"]),
        color=hexColours["falconRed"]
    )

    notifEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])
    notifEmbed.set_author(name="Launch #{}".format(nextLaunchJSON["flight_number"]))

    UTCDate = await getUTCFromTimestamp(nextLaunchJSON["launch_date_unix"])
    notifEmbed.add_field(name="Launch date", value=UTCDate)

    return notifEmbed
