from discord import Embed

from modules.structure import UTCFromTS
from modules.statics import falconRed, rocketIDImages, generalErrorEmbed, ownerMention

payloadInfo = """Type: {}
Orbit: {}
Mass: {}
Manufacturer: {}
Customer{}: {}
"""
coreInfo = """Serial: {}
Flight: {}
Landing: {}
Landing Type: {}
Landing Vehicle: {}
"""
launchDateInfo = """{}
Precision: {}
"""


async def genLaunchInfoEmbeds(nextLaunchJSON):
    launchInfoEmbed = Embed(
        color=falconRed,
        description=nextLaunchJSON["details"],
        title="Launch #{} - {}".format(
            nextLaunchJSON["flight_number"], nextLaunchJSON["mission_name"]
        ),
    )

    # Set thumbnail depending on rocket ID
    if nextLaunchJSON["rocket"]["rocket_id"] in rocketIDImages:
        launchInfoEmbed.set_thumbnail(
            url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]]
        )

    launchInfoEmbed.add_field(
        name="Launch vehicle",
        value="{} {}".format(
            nextLaunchJSON["rocket"]["rocket_name"],
            nextLaunchJSON["rocket"]["rocket_type"],
        ),
    )

    # Add a field for the launch date
    UTCLaunchDate = await UTCFromTS(nextLaunchJSON["launch_date_unix"])
    launchInfoEmbed.add_field(
        name="Launch date",
        value=launchDateInfo.format(
            UTCLaunchDate, nextLaunchJSON["tentative_max_precision"]
        ),
    )

    discussionURL = nextLaunchJSON["links"]["reddit_campaign"]
    if discussionURL != None:
        launchInfoEmbed.add_field(name="r/SpaceX discussion", value=discussionURL)

    launchInfoEmbed.add_field(
        name="Launch site", value=nextLaunchJSON["launch_site"]["site_name_long"]
    )

    if nextLaunchJSON["rocket"]["rocket_id"] == "falcon9":
        # TODO: ALlow "Core Info" section for FH
        # Falcon 9 always has 1 core, FH (or others) will be different
        launchInfoEmbed.add_field(
            name="Core info",
            value=coreInfo.format(
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["core_serial"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["flight"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["landing_intent"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["landing_type"],
                nextLaunchJSON["rocket"]["first_stage"]["cores"][0]["landing_vehicle"],
            ),
        )

    # Add a field for each payload, with basic information
    for payload in nextLaunchJSON["rocket"]["second_stage"]["payloads"]:
        launchInfoEmbed.add_field(
            name="Payload: {}".format(payload["payload_id"]),
            value=payloadInfo.format(
                payload["payload_type"],
                payload["orbit"],
                payload["payload_mass_kg"],
                payload["manufacturer"],
                "(s)" if len(payload["customers"]) > 1 else "",
                ", ".join(payload["customers"]),
            ),
        )

    return launchInfoEmbed


async def genLaunchingSoonEmbed(nextLaunchJSON):
    UTCLaunchDate = await UTCFromTS(nextLaunchJSON["launch_date_unix"])
    embedDesc = ""

    notifEmbed = Embed(
        color=falconRed,
        title="{} is launching soon!".format(nextLaunchJSON["mission_name"]),
    )

    if nextLaunchJSON["links"]["mission_patch_small"] != None:
        notifEmbed.set_thumbnail(url=nextLaunchJSON["links"]["mission_patch_small"])
    elif nextLaunchJSON["rocket"]["rocket_id"] in rocketIDImages:
        notifEmbed.set_thumbnail(
            url=rocketIDImages[nextLaunchJSON["rocket"]["rocket_id"]]
        )

    # Embed links [using](markdown)
    if nextLaunchJSON["links"]["video_link"] != None:
        embedDesc += f"[Livestream]({nextLaunchJSON['links']['video_link']})\n"
    if nextLaunchJSON["links"]["reddit_launch"] != None:
        embedDesc += (
            f"[r/SpaceX Launch Thread]({nextLaunchJSON['links']['reddit_launch']})\n"
        )
    if nextLaunchJSON["links"]["presskit"] != None:
        embedDesc += f"[Press kit]({nextLaunchJSON['links']['presskit']})\n"
    notifEmbed.description = embedDesc

    notifEmbed.add_field(name="Launch date", value=UTCLaunchDate)

    return notifEmbed


async def getInfoEmbed():
    """
    Info ideas:
    - Developer / Owner tag
    - Guild, Channel, and User count
    - Uptime
    - Github link
    - Invite link
    - Bot metrics (command count, avg commands per ?, etc.)
    - API latency?
    - Let user know about !help
    """
    infoEmbed = Embed(
        title="SpaceX-Launch-Bot Information",
        color=falconRed,
        description="A Discord bot for getting news, information, and notifications about upcoming SpaceX launches",
    )
    infoEmbed.add_field(
        name="Links", value="[GitHub](https://github.com/r-spacex/SpaceX-Launch-Bot)"
    )
    infoEmbed.add_field(name="Contact", value=f"{ownerMention}")
    infoEmbed.add_field(
        name="Help", value="Use the command !help to get a list of commands"
    )
    return infoEmbed
