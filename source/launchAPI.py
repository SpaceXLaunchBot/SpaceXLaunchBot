from discord import Embed
import datetime
import asyncio
import aiohttp

rocketIDImages = {
    "falcon9": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/falcon9.png",
    "falconheavy": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/falconHeavy.png",
    "falcon1": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/logo.jpg"
}
hexColours = {
    "errorRed": 0xFF0000,
    "falconRed": 0xEE0F46
}
upcomingLaunchesURL = "https://api.spacexdata.com/v2/launches/upcoming?order=asc"
APIErrorEmbed = Embed(title="Error", description="SpaceX API error, contact @Dragon#0571", color=hexColours["errorRed"])

async def getnextLaunchJSON():
    """
    Using aiohttp, grab the latest launch info
    Returns 0 if fail
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(upcomingLaunchesURL) as response:
            if response.status != 200:
                return 0
            return list(await response.json())[0]

async def getnextLaunchEmbed(nextLaunchJSON):
    # Create embed & insert reddit discussion link + simple description
    launchEmbed = Embed(
        title="r/SpaceX Discussion",
        url = nextLaunchJSON["links"]["reddit_campaign"],
        description="A {} rocket carrying {} payload(s), launching from {}".format(
            nextLaunchJSON["rocket"]["rocket_name"],
            len(nextLaunchJSON["rocket"]["second_stage"]["payloads"]),
            nextLaunchJSON["launch_site"]["site_name_long"]
        ),
        color=hexColours["falconRed"]
    )

    # Set thumbnail depending on rocked ID & set the authoor to the launch no.
    launchEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])
    launchEmbed.set_author(name="Launch #{}".format(nextLaunchJSON["flight_number"]))

    # Add a field for the launch date
    launchingOn = "To Be Announced"
    unixDate = nextLaunchJSON["launch_date_unix"]
    if unixDate != "null":
        formattedDate = datetime.datetime.fromtimestamp(unixDate).strftime('%Y-%m-%d %H:%M:%S')
        launchingOn = "{} UTC".format(formattedDate)
    launchEmbed.add_field(name="Launching on", value=launchingOn)

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

    return launchEmbed

async def getLiteEmbed(nextLaunchJSON):
    # A "lite" version of the embed that should never reach the embed size limit
    launchEmbed = Embed(
        title="r/SpaceX Discussion",
        url = nextLaunchJSON["links"]["reddit_campaign"],
        description="This information has been reduced as the data is too large to contain in this embed",
        color=hexColours["falconRed"]
    )

    # Set thumbnail depending on rocked ID & set the authoor to the launch no.
    launchEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])
    launchEmbed.set_author(name="Launch #{}".format(nextLaunchJSON["flight_number"]))

    # Info in new field
    launchEmbed.add_field(name="Information", value="A {} rocket carrying {} payload(s), launching from {}".format(
        nextLaunchJSON["rocket"]["rocket_name"],
        len(nextLaunchJSON["rocket"]["second_stage"]["payloads"]),
        nextLaunchJSON["launch_site"]["site_name_long"]
    ))

    # Add a field for the launch date
    unixDate = int(nextLaunchJSON["launch_date_unix"])
    formattedDate = datetime.datetime.fromtimestamp(unixDate).strftime('%Y-%m-%d %H:%M:%S')
    launchEmbed.add_field(name="Launching on", value="{} UTC".format(formattedDate))

    return launchEmbed
