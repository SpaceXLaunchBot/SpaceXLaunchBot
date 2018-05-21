"""
Contains functions for generating/creating embeds about launches to send to users
Note: f-strings aren't used in this module as .format is nicer for larger strings
"""

from copy import deepcopy
from discord import Embed

from modules.utils import UTCFromTimestamp
from modules.colours import hexColours

rocketIDImages = {
    "falcon9": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/falcon9.png",
    "falconheavy": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/falconHeavy.png",
    "falcon1": "https://raw.githubusercontent.com/thatguywiththatname/SpaceX-Launch-Bot/master/source/resources/images/logo.jpg"
}

# TODO: Add checks for empty fields in Embeds: empty fields = HTTPException

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
    if reusing == []:
        reusing = ["None"]  # Can't have empty fields
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
    """
    TODO: Test why thumbnail sometimes isn't set
    Sometimes a thumbnail is not set (or atleast not shown?) in the embed, causing a notification to be sent
    out about new launch info, when actually the only thing that is different is that the thumbnail did not
    set properly / show up properly
    """
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
    UTCDate = await UTCFromTimestamp(nextLaunchJSON["launch_date_unix"])
    launchEmbed.add_field(name="Launch date", value=UTCDate)

    return launchEmbed

async def getLaunchNotifEmbed(nextLaunchJSON):
    notifEmbed = Embed(color=hexColours["falconRed"])

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

    UTCDate = await UTCFromTimestamp(nextLaunchJSON["launch_date_unix"])
    notifEmbed.add_field(name="Launch date", value=UTCDate)

    if nextLaunchJSON["links"]["reddit_launch"] != None:
        # TODO: Shorten this to just reddit.com/ID instead of the whole link (looks better)
        notifEmbed.add_field(name="r/SpaceX Launch Thread", value=nextLaunchJSON["links"]["reddit_launch"])

    if nextLaunchJSON["links"]["presskit"] != None:
        notifEmbed.add_field(name="Press kit", value=nextLaunchJSON["links"]["presskit"])
    
    return notifEmbed
