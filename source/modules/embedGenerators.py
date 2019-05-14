from copy import deepcopy
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


async def gen_launch_info_embeds(next_launch_dict):

    # Having desc set to `None` breaks things
    if next_launch_dict["details"] == None:
        next_launch_dict["details"] = ""

    launch_info_embed = Embed(
        color=falconRed,
        description=next_launch_dict["details"],
        title="Launch #{} - {}".format(
            next_launch_dict["flight_number"], next_launch_dict["mission_name"]
        ),
    )

    # Set thumbnail depending on rocket ID
    if next_launch_dict["rocket"]["rocket_id"] in rocketIDImages:
        launch_info_embed.set_thumbnail(
            url=rocketIDImages[next_launch_dict["rocket"]["rocket_id"]]
        )

    launch_info_embed.add_field(
        name="Launch vehicle",
        value="{} {}".format(
            next_launch_dict["rocket"]["rocket_name"],
            next_launch_dict["rocket"]["rocket_type"],
        ),
    )

    # Add a field for the launch date
    UTCLaunchDate = await UTCFromTS(next_launch_dict["launch_date_unix"])
    launch_info_embed.add_field(
        name="Launch date",
        value=launchDateInfo.format(
            UTCLaunchDate, next_launch_dict["tentative_max_precision"]
        ),
    )

    # Basic embed structure built, copy into small version
    launch_info_embedSmall = deepcopy(launch_info_embed)

    discussionURL = next_launch_dict["links"]["reddit_campaign"]
    if discussionURL != None:
        launch_info_embed.add_field(name="r/SpaceX discussion", value=discussionURL)

    launch_info_embed.add_field(
        name="Launch site", value=next_launch_dict["launch_site"]["site_name_long"]
    )

    if next_launch_dict["rocket"]["rocket_id"] == "falcon9":
        # TODO: ALlow "Core Info" section for FH
        # Falcon 9 always has 1 core, FH (or others) will be different
        launch_info_embed.add_field(
            name="Core info",
            value=coreInfo.format(
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["core_serial"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["flight"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["landing_intent"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["landing_type"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0][
                    "landing_vehicle"
                ],
            ),
        )

    # Add a field for each payload, with basic information
    for payload in next_launch_dict["rocket"]["second_stage"]["payloads"]:
        launch_info_embed.add_field(
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

    if len(launch_info_embed.title) > 256:
        # Title too big to send, no way around this other than send an err
        return generalErrorEmbed
    elif len(launch_info_embed) > 2048:
        # If body is too big, send small embed
        return launch_info_embedSmall
    return launch_info_embed


async def genLaunchingSoonEmbed(next_launch_dict):
    embedDesc = ""

    notifEmbed = Embed(
        color=falconRed,
        title="{} is launching soon!".format(next_launch_dict["mission_name"]),
    )

    if next_launch_dict["links"]["mission_patch_small"] != None:
        notifEmbed.set_thumbnail(url=next_launch_dict["links"]["mission_patch_small"])
    elif next_launch_dict["rocket"]["rocket_id"] in rocketIDImages:
        notifEmbed.set_thumbnail(
            url=rocketIDImages[next_launch_dict["rocket"]["rocket_id"]]
        )

    # Embed links [using](markdown)
    if next_launch_dict["links"]["video_link"] != None:
        embedDesc += f"[Livestream]({next_launch_dict['links']['video_link']})\n"
    if next_launch_dict["links"]["reddit_launch"] != None:
        embedDesc += (
            f"[r/SpaceX Launch Thread]({next_launch_dict['links']['reddit_launch']})\n"
        )
    if next_launch_dict["links"]["presskit"] != None:
        embedDesc += f"[Press kit]({next_launch_dict['links']['presskit']})\n"
    notifEmbed.description = embedDesc

    UTCLaunchDate = await UTCFromTS(next_launch_dict["launch_date_unix"])
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
