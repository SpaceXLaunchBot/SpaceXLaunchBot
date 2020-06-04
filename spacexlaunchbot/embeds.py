from typing import Dict, List

import discord

import config
import utils

# TODO: Have function that validates size of embed
#  See https://discord.com/developers/docs/resources/channel#embed-limits

# Use Github as image hosting
IMAGE_BASE_URL = (
    "https://raw.githubusercontent.com/r-spacex/SpaceXLaunchBot/master/images/logos"
)

# A map of rocket id (in the API) to the image to represent it
ROCKET_ID_IMAGES = {
    "falcon9": f"{IMAGE_BASE_URL}/falcon_9.png",
    "falconheavy": f"{IMAGE_BASE_URL}/falcon_heavy.png",
    "falcon1": f"{IMAGE_BASE_URL}/logo.jpg",
}

# Templates for embed fields
PAYLOAD_INFO = "Type: {}\nOrbit: {}\nMass: {}\nManufacturer: {}\nCustomer{}: {}"
CORE_INFO = (
    "Serial: {}\nFlight: {}\nLanding: {}\nLanding Type: {}\nLanding Location: {}"
)


class EmbedWithFields(discord.Embed):
    def __init__(self, fields: List[List[str]], inline_all: bool = True, **kwargs):
        """Takes the discord.Embed class and allows you to define fields immediately.

        Args:
            fields : A list of pairs of strings, the name and text of each field.
            inline_all : Whether or not to inline all of the fields.

        """
        super().__init__(**kwargs)
        for field in fields:
            self.add_field(name=field[0], value=field[1], inline=inline_all)


def md_link(name: str, url: str) -> str:
    """Makes strings easier to read when defining markdown links."""
    return f"[{name}]({url})"


async def create_launch_info_embed(launch_info: Dict) -> discord.Embed:
    """Creates a "launch information" style embed from a dict of launch information.

    Args:
        launch_info: A dictionary of launch information from apis.spacex.

    Returns:
        A Discord.Embed object.

    """
    launch_date_str = await utils.utc_from_ts(launch_info["launch_date_unix"])

    fields = [
        [
            "Launch Vehicle",
            f'{launch_info["rocket"]["rocket_name"]} {launch_info["rocket"]["rocket_type"]}',
        ],
        [
            "Launch Date (UTC)",
            f'{launch_date_str}\nPrecision: {launch_info["tentative_max_precision"]}',
        ],
        ["Launch Site", launch_info["launch_site"]["site_name_long"]],
    ]

    for core_dict in launch_info["rocket"]["first_stage"]["cores"]:
        fields.append(
            [
                f"Core Info",
                CORE_INFO.format(
                    core_dict["core_serial"],
                    core_dict["flight"],
                    core_dict["landing_intent"],
                    core_dict["landing_type"],
                    core_dict["landing_vehicle"],
                ),
            ]
        )

    # Add a field for each payload, with basic information
    for payload in launch_info["rocket"]["second_stage"]["payloads"]:
        fields.append(
            [
                f'Payload: {payload["payload_id"]}',
                PAYLOAD_INFO.format(
                    payload["payload_type"],
                    payload["orbit"],
                    payload["payload_mass_kg"],
                    payload["manufacturer"],
                    "(s)" if len(payload["customers"]) > 1 else "",
                    ", ".join(payload["customers"]),
                ),
            ]
        )

    launch_info_embed = EmbedWithFields(
        color=config.COLOUR_FALCON_RED,
        description=(
            f'{launch_info["details"] or ""} '
            + f'{md_link("Click for r/SpaceX Thread", launch_info["links"]["reddit_campaign"])}.'
        ),
        title=f'Launch #{launch_info["flight_number"]} - {launch_info["mission_name"]}',
        fields=fields,
    )

    if (patch_url := launch_info["links"]["mission_patch_small"]) is not None:
        launch_info_embed.set_thumbnail(url=patch_url)
    elif (rocket_img_url := launch_info["rocket"]["rocket_id"]) in ROCKET_ID_IMAGES:
        launch_info_embed.set_thumbnail(url=rocket_img_url)

    return launch_info_embed


async def create_launching_soon_embed(launch_info: Dict) -> discord.Embed:
    """Create a "launching soon" style embed from a dict of launch information.

    Args:
        launch_info: A dictionary of launch information from apis.spacex.

    Returns:
        A Discord.Embed object.

    """

    embed_desc = ""
    utc_launch_date = await utils.utc_from_ts(launch_info["launch_date_unix"])

    if (video_url := launch_info["links"]["video_link"]) is not None:
        embed_desc += md_link("Livestream", video_url) + "\n"

    if (reddit_url := launch_info["links"]["reddit_launch"]) is not None:
        embed_desc += md_link("r/SpaceX Launch Thread", reddit_url) + "\n"

    if (press_kit_url := launch_info["links"]["presskit"]) is not None:
        embed_desc += md_link("Press kit", press_kit_url) + "\n"

    notif_embed = EmbedWithFields(
        title="{} is launching soon!".format(launch_info["mission_name"]),
        description=embed_desc,
        color=config.COLOUR_FALCON_RED,
        fields=[["Launch date (UTC)", utc_launch_date]],
    )

    if (patch_url := launch_info["links"]["mission_patch_small"]) is not None:
        notif_embed.set_thumbnail(url=patch_url)
    elif (rocket_img_url := launch_info["rocket"]["rocket_id"]) in ROCKET_ID_IMAGES:
        notif_embed.set_thumbnail(url=rocket_img_url)

    return notif_embed


def create_bot_info_embed(guild_count: int, subbed_channel_count: int) -> discord.Embed:
    """Creates an info embed.

    Args:
        guild_count: The number of guilds the bot is currently a member of.
        subbed_channel_count: The number of currently subscribed channels.

    Returns:
        A discord.Embed object.

    """
    return EmbedWithFields(
        title="SpaceXLaunchBot Information",
        color=config.COLOUR_FALCON_RED,
        description="A Discord bot for getting news, information, and notifications "
        "about upcoming SpaceX launches",
        fields=[
            ["Guild Count", f"{guild_count}"],
            ["Subscribed Channel Count", f"{subbed_channel_count}"],
            [
                "Links",
                f'{md_link("Github", config.BOT_GITHUB)}, {md_link("Bot Invite", config.BOT_INVITE_URL)}',
            ],
            ["Contact", f"{config.BOT_OWNER}"],
            [
                "Help",
                f"Use `{config.BOT_COMMAND_PREFIX} help` to get a list of commands",
            ],
        ],
    )


HELP_EMBED = EmbedWithFields(
    title="SpaceXLaunchBot Commands",
    description=f"Command prefix: {config.BOT_COMMAND_PREFIX}",
    color=config.COLOUR_FALCON_RED,
    inline_all=False,
    fields=[
        [
            "nextlaunch",
            "Send the latest launch information message to the current channel",
        ],
        [
            "addchannel",
            "Add the current channel to the notification service\n*Only admins can use this command*",
        ],
        [
            "removechannel",
            "Remove the current channel from the notification service\n*Only admins can use this command*",
        ],
        [
            "setmentions @mention",
            'Set roles/users to be mentioned when a "launching soon" message is sent. Can be formatted with multiple mentions in any order, like this: `slb setmentions @role1 @user1 @here`. Calling `setmentions` multiple times will not stack the mentions, it will just overwrite your previous mentions\n*Only admins can use this command*',
        ],
        [
            "removementions",
            "Remove all mentions set for the current guild\n*Only admins can use this command*",
        ],
        [
            "getmentions",
            'Show the mentions you have set for "launching soon" notifications\n*Only admins can use this command*',
        ],
        ["info", "Send information about the bot to the current channel"],
        ["help", "List these commands"],
    ],
)

API_ERROR_EMBED = discord.Embed(
    title="Error",
    description=f"An API error occurred, contact {config.BOT_OWNER}",
    color=config.COLOUR_ERROR_RED,
)

GENERAL_ERROR_EMBED = discord.Embed(
    title="Error",
    description=f"An error occurred, contact {config.BOT_OWNER}",
    color=config.COLOUR_ERROR_RED,
)

LEGACY_PREFIX_WARNING_EMBED = discord.Embed(
    title="New Prefix In Use",
    description="You used a command with the old prefix (!), SpaceXLaunchBot has "
    'moved to using "slb" as a prefix, e.g. `slb help`. This warning will be removed '
    "soon.",
    color=config.COLOUR_INFO_ORANGE,
)
