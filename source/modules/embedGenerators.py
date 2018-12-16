"""
Stuff for generating/creating embeds about launches to send to users
"""

from copy import deepcopy
from discord import Embed

from modules.structure import launchTimeFromTS
from modules.statics import falconRed, rocketIDImages

payloadInfo = \
"""Type: {}
Orbit: {}
Mass: {}
Manufacturer(s): {}
Customer(s): {}
"""
coreInfo = \
"""Serial: {}
Flight: {}
Landing: {}
Landing Type: {}
Landing Vehicle: {}
"""
launchDateInfo = \
"""{}
Precision: {}
"""

async def genLaunchInfoEmbeds(nextLaunchJSON):
   
    launchInfoEmbed = Embed(
        color=falconRed,
        description=nextLaunchJSON["details"],
        title = "Launch #{} - {}".format(
            nextLaunchJSON["flight_number"],
            nextLaunchJSON["mission_name"]
    ))

    # Set thumbnail depending on rocket ID
    launchInfoEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])

    launchInfoEmbed.add_field(
        name="Launch vehicle",
        value="{} {}".format(
            nextLaunchJSON["rocket"]["rocket_name"],
            nextLaunchJSON["rocket"]["rocket_type"]
    ))

    # Add a field for the launch date  
    UTCLaunchDate = await launchTimeFromTS(nextLaunchJSON["launch_date_unix"])
    launchInfoEmbed.add_field(
        name="Launch date",
        value=launchDateInfo.format(
            UTCLaunchDate,
            nextLaunchJSON["tentative_max_precision"]
    ))

    # Basic embed structure built, copy into small version
    launchInfoEmbedSmall = deepcopy(launchInfoEmbed)

    discussionURL = nextLaunchJSON["links"]["reddit_campaign"]    
    if discussionURL != None:
        launchInfoEmbed.add_field(name="r/SpaceX discussion", value=discussionURL)
    
    launchInfoEmbed.add_field(name="Launch site", value=nextLaunchJSON["launch_site"]["site_name_long"])

    if nextLaunchJSON["rocket"]["rocket_id"] == "falcon9":
        # Falcon 9 always has 1 core, FH (or others) will be different
        launchInfoEmbed.add_field(
            name="Core info",
            value=coreInfo.format(
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["core_serial"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["flight"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["landing_intent"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["landing_type"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["landing_vehicle"]
        ))

    # Add a field for each payload, with basic information
    for payload in nextLaunchJSON["rocket"]["second_stage"]["payloads"]:
        launchInfoEmbed.add_field(
            name="Payload: {}".format(payload["payload_id"]),
            value=payloadInfo.format(
                payload["payload_type"],
                payload["orbit"],
                payload["payload_mass_kg"],
                payload["manufacturer"],
                ", ".join(payload["customers"])
        ))

    return launchInfoEmbed, launchInfoEmbedSmall

async def genLaunchingSoonEmbed(nextLaunchJSON):
    UTCLaunchDate = await launchTimeFromTS(nextLaunchJSON["launch_date_unix"])
    embedDesc = ""

    notifEmbed = Embed(
        color=falconRed,
        title="{} is launching soon!".format(nextLaunchJSON["mission_name"])
    )
    
    if nextLaunchJSON["links"]["mission_patch_small"] != None:
        notifEmbed.set_thumbnail(url=nextLaunchJSON["links"]["mission_patch_small"])
    else:
        notifEmbed.set_thumbnail(url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]])
    
    notifEmbed.add_field(name="Launch date", value=UTCLaunchDate)
    
    if nextLaunchJSON["links"]["video_link"] != None:
        embedDesc += f"[Livestream]({nextLaunchJSON['links']['video_link']})"
    if nextLaunchJSON["links"]["reddit_launch"] != None:
        embedDesc += f"[r/SpaceX Launch Thread]({nextLaunchJSON['links']['reddit_launch']})"
    if nextLaunchJSON["links"]["presskit"] != None:
        embedDesc += f"[Press kit]({nextLaunchJSON['links']['presskit']})"
    notifEmbed.description = embedDesc

    return notifEmbed
