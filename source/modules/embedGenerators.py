"""
Stuff for generating/creating embeds about launches to send to users
"""

from copy import deepcopy
from discord import Embed

from modules.structure import launchTimeFromTS
from modules.statics import falconRed, rocketIDImages

async def genLaunchInfoEmbeds(nextLaunchJSON):
    embedTitle = "r/SpaceX Discussion"
    numPayloads = len(nextLaunchJSON["rocket"]["second_stage"]["payloads"])
    UTCLaunchDate = await launchTimeFromTS(nextLaunchJSON["launch_date_unix"])

    if nextLaunchJSON["links"]["reddit_campaign"] == None:
        embedTitle = "No discussion URL"

    launchEmbed = Embed(
        title=embedTitle,
        url=nextLaunchJSON["links"]["reddit_campaign"],
        color=falconRed,
        description="A {} carrying {} payload{}, launching from {}".format(
            nextLaunchJSON["rocket"]["rocket_name"],
            numPayloads,
            "" if numPayloads < 2 else "s",
            nextLaunchJSON["launch_site"]["site_name_long"]
        )
    )

    # Set thumbnail depending on rocket ID
    launchEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])
    launchEmbed.set_author(name="Launch #{} - {}".format(
        nextLaunchJSON["flight_number"],
        nextLaunchJSON["mission_name"]
    ))

    # Add a field for the launch date  
    launchEmbed.add_field(name="Launch date", value=UTCLaunchDate)

    # Basic embed structure built, copy into small version
    launchEmbedSmall = deepcopy(launchEmbed)
   
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

    return launchEmbed, launchEmbedSmall

async def genLaunchingSoonEmbed(nextLaunchJSON):
    UTCLaunchDate = await launchTimeFromTS(nextLaunchJSON["launch_date_unix"])
    notifEmbed = Embed(color=falconRed)
    
    notifEmbed.set_author(name="{} is launching soon!".format(nextLaunchJSON["mission_name"]))
    
    if nextLaunchJSON["links"]["video_link"] != None:
        notifEmbed.title= "Livestream"
        notifEmbed.url = nextLaunchJSON["links"]["video_link"]
    else:
        notifEmbed.title="r/SpaceX Discussion"
        notifEmbed.url = nextLaunchJSON["links"]["reddit_campaign"]

    if nextLaunchJSON["links"]["mission_patch_small"] != None:
        notifEmbed.set_thumbnail(url=nextLaunchJSON["links"]["mission_patch_small"])
    else:
        notifEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])

    notifEmbed.add_field(name="Launch date", value=UTCLaunchDate)

    if nextLaunchJSON["links"]["reddit_launch"] != None:
        notifEmbed.add_field(name="r/SpaceX Launch Thread", value=nextLaunchJSON["links"]["reddit_launch"])

    if nextLaunchJSON["links"]["presskit"] != None:
        notifEmbed.add_field(name="Press kit", value=nextLaunchJSON["links"]["presskit"])
    
    return notifEmbed
