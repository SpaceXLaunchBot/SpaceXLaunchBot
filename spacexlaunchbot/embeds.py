import random
from typing import Dict, List

import discord

from . import config
from .utils import md_link, utc_from_ts

# A couple of pylint rules we want in the rest of the project are broken in this file.
# superfluous-parens is erroneously picked up when := is used after an elif?
# pylint: disable=line-too-long,superfluous-parens

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
PAYLOAD_INFO = "Type: {}\nOrbit: {}\nMass: {}kg\nManufacturer: {}\nCustomer{}: {}"


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


def embed_is_valid(embed: discord.Embed) -> bool:
    """Determines if an embed is within the size limits for discord.

    See https://discord.com/developers/docs/resources/channel#embed-limits.

    Args:
        embed: The discord.Embed object to validate.

    Returns:
        True if it is within size limits, otherwise False.

    """
    if len(embed.fields) > 25:
        return False

    total_len = 0
    comparisons = [
        [len(embed.title), 256],
        [len(embed.description), 2048],
        [len(embed.footer), 2048],
        [len(embed.author.name), 256],
    ]

    for length, limit in comparisons:
        if length > limit:
            return False
        total_len += length

    for field in embed.fields:
        if (name_length := len(field.name)) > 256 or (
            value_length := len(field.value)
        ) > 1024:
            return False

        total_len += name_length + value_length

    if total_len > 6000:
        return False

    return True


async def create_launch_info_embed(launch_info: Dict) -> discord.Embed:
    """Creates a "launch information" style embed from a dict of launch information.

    Args:
        launch_info: A dictionary of launch information from apis.spacex.

    Returns:
        A Discord.Embed object.

    """
    launch_date_str = utc_from_ts(launch_info["launch_date_unix"])

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
        core_info = f'Serial: {core_dict["core_serial"]}\nFlight: {core_dict["flight"]}'

        if core_dict["landing_intent"] is False:
            core_info += "\nLanding: No"
        else:
            core_info += f'\nLanding: Yes\nLanding Type: {core_dict["landing_type"]}'
            core_info += f'\nLanding Location: {core_dict["landing_vehicle"]}'

        fields.append(["Core Info", core_info])

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
        description=launch_info["details"] or "",
        title=f'Launch #{launch_info["flight_number"]} - {launch_info["mission_name"]}',
        fields=fields,
    )

    if (reddit_url := launch_info["links"]["reddit_campaign"]) is not None:
        launch_info_embed.description += (
            f' {md_link("Click for r/SpaceX Thread", reddit_url)}.'
        )

    if (patch_url := launch_info["links"]["mission_patch_small"]) is not None:
        launch_info_embed.set_thumbnail(url=patch_url)
    elif (rocket_img_url := launch_info["rocket"]["rocket_id"]) in ROCKET_ID_IMAGES:
        launch_info_embed.set_thumbnail(url=rocket_img_url)

    if (flickr_urls := launch_info["links"]["flickr_images"]) is not None:
        launch_info_embed.set_image(url=random.choice(flickr_urls))  # nosec

    return launch_info_embed


async def create_launching_soon_embed(launch_info: Dict) -> discord.Embed:
    """Create a "launching soon" style embed from a dict of launch information.

    Args:
        launch_info: A dictionary of launch information from apis.spacex.

    Returns:
        A Discord.Embed object.

    """
    embed_desc = ""
    utc_launch_date = utc_from_ts(launch_info["launch_date_unix"])

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

LEGACY_PREFIX_WARNING_EMBED = discord.Embed(
    title="New Prefix In Use",
    description="You used a command with the old prefix (!), SpaceXLaunchBot has "
    'moved to using "slb" as a prefix, e.g. `slb help`. This warning will be removed '
    "soon.",
    color=config.COLOUR_INFO_ORANGE,
)
