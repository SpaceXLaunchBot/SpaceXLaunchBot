import copy
from typing import Dict

import discord

import config
import statics
import utils
from dbs.redisclient import redis

PAYLOAD_INFO = """Type: {}
Orbit: {}
Mass: {}
Manufacturer: {}
Customer{}: {}
"""
CORE_INFO = """Serial: {}
Flight: {}
Landing: {}
Landing Type: {}
Landing Vehicle: {}
"""
LAUNCH_DATE_INFO = """{}
Precision: {}
"""

BOT_INVITE = (
    "https://discordapp.com/oauth2/authorize?scope=bot"
    f"&client_id={config.BOT_CLIENT_ID}&permissions={config.BOT_INVITE_PERMISSIONS}"
)


async def get_launch_info_embed(launch_dict: Dict) -> discord.Embed:
    """Creates a "launch information" style embed from a dict of launch information.

    Args:
        launch_dict: A dictionary of launch information from apis.spacex.

    Returns:
        A Discord.Embed object.

    """

    # Having desc set to `None` breaks things
    if launch_dict["details"] is None:
        launch_dict["details"] = ""

    launch_info_embed = discord.Embed(
        color=statics.FALCON_RED,
        description=launch_dict["details"],
        title="Launch #{} - {}".format(
            launch_dict["flight_number"], launch_dict["mission_name"]
        ),
    )

    # Set thumbnail depending on rocket ID, use mission patch if available
    if launch_dict["links"]["mission_patch_small"] is not None:
        launch_info_embed.set_thumbnail(url=launch_dict["links"]["mission_patch_small"])
    elif launch_dict["rocket"]["rocket_id"] in statics.ROCKET_ID_IMAGES:
        launch_info_embed.set_thumbnail(
            url=statics.ROCKET_ID_IMAGES[launch_dict["rocket"]["rocket_id"]]
        )

    launch_info_embed.add_field(
        name="Launch vehicle",
        value="{} {}".format(
            launch_dict["rocket"]["rocket_name"], launch_dict["rocket"]["rocket_type"]
        ),
    )

    # Add a field for the launch date
    utc_launch_date = await utils.utc_from_ts(launch_dict["launch_date_unix"])
    launch_info_embed.add_field(
        name="Launch date",
        value=LAUNCH_DATE_INFO.format(
            utc_launch_date, launch_dict["tentative_max_precision"]
        ),
    )

    # Basic embed structure built, copy into small version
    launch_info_embed_small = copy.deepcopy(launch_info_embed)

    discussion_url = launch_dict["links"]["reddit_campaign"]
    if discussion_url is not None:
        launch_info_embed.add_field(name="r/SpaceX discussion", value=discussion_url)

    launch_info_embed.add_field(
        name="Launch site", value=launch_dict["launch_site"]["site_name_long"]
    )

    if launch_dict["rocket"]["rocket_id"] == "falcon9":
        # Falcon 9 always has 1 core, FH (or others) will be different
        launch_info_embed.add_field(
            name="Core info",
            value=CORE_INFO.format(
                launch_dict["rocket"]["first_stage"]["cores"][0]["core_serial"],
                launch_dict["rocket"]["first_stage"]["cores"][0]["flight"],
                "Yes"
                if launch_dict["rocket"]["first_stage"]["cores"][0]["landing_intent"]
                else "No",
                launch_dict["rocket"]["first_stage"]["cores"][0]["landing_type"],
                launch_dict["rocket"]["first_stage"]["cores"][0]["landing_vehicle"],
            ),
        )

    elif launch_dict["rocket"]["rocket_id"] == "falconheavy":
        for core_num, core_dict in enumerate(
            launch_dict["rocket"]["first_stage"]["cores"]
        ):
            launch_info_embed.add_field(
                name=f"Core {core_num} info",
                value=CORE_INFO.format(
                    core_dict["core_serial"],
                    core_dict["flight"],
                    core_dict["landing_intent"],
                    core_dict["landing_type"],
                    core_dict["landing_vehicle"],
                ),
            )

    # Add a field for each payload, with basic information
    for payload in launch_dict["rocket"]["second_stage"]["payloads"]:
        launch_info_embed.add_field(
            name="Payload: {}".format(payload["payload_id"]),
            value=PAYLOAD_INFO.format(
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
        return statics.GENERAL_ERROR_EMBED
    if len(launch_info_embed) > 2048:
        # If body is too big, send small embed
        return launch_info_embed_small
    return launch_info_embed


async def get_launching_soon_embed(launch_dict: Dict) -> discord.Embed:
    """Create a "launching soon" style embed from a dict of launch information.

    Args:
        launch_dict: A dictionary of launch information from apis.spacex.

    Returns:
        A Discord.Embed object.

    """

    embed_desc = ""

    notif_embed = discord.Embed(
        color=statics.FALCON_RED,
        title="{} is launching soon!".format(launch_dict["mission_name"]),
    )

    if launch_dict["links"]["mission_patch_small"] is not None:
        notif_embed.set_thumbnail(url=launch_dict["links"]["mission_patch_small"])
    elif launch_dict["rocket"]["rocket_id"] in statics.ROCKET_ID_IMAGES:
        notif_embed.set_thumbnail(
            url=statics.ROCKET_ID_IMAGES[launch_dict["rocket"]["rocket_id"]]
        )

    # Embed links [using](markdown)
    if launch_dict["links"]["video_link"] is not None:
        embed_desc += f"[Livestream]({launch_dict['links']['video_link']})\n"
    if launch_dict["links"]["reddit_launch"] is not None:
        embed_desc += (
            f"[r/SpaceX Launch Thread]({launch_dict['links']['reddit_launch']})\n"
        )
    if launch_dict["links"]["presskit"] is not None:
        embed_desc += f"[Press kit]({launch_dict['links']['presskit']})\n"
    notif_embed.description = embed_desc

    utc_launch_date = await utils.utc_from_ts(launch_dict["launch_date_unix"])
    notif_embed.add_field(name="Launch date", value=utc_launch_date)

    return notif_embed


async def get_info_embed(guild_count: int) -> discord.Embed:
    """Creates an info embed.

    Args:
        guild_count: The number of guilds the bot is currently a member of.

    Returns:
        A discord.Embed object.

    """
    subbed_channel_count = await redis.subbed_channels_count()

    info_embed = discord.Embed(
        title="SpaceXLaunchBot Information",
        color=statics.FALCON_RED,
        description="A Discord bot for getting news, information, and notifications "
        "about upcoming SpaceX launches",
    )

    info_embed.add_field(name="Guild Count", value=f"{guild_count}")
    info_embed.add_field(
        name="Subscribed Channel Count", value=f"{subbed_channel_count}"
    )
    info_embed.add_field(
        name="Links", value=f"[GitHub]({config.BOT_GITHUB}), [Bot Invite]({BOT_INVITE})"
    )
    info_embed.add_field(name="Contact", value=f"{config.BOT_OWNER}")
    info_embed.add_field(
        name="Help",
        value=f"Use {config.BOT_COMMAND_PREFIX}help to get a list of commands",
    )

    return info_embed
