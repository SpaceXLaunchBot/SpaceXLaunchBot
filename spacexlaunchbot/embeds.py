import random
from typing import Dict, List

import discord

from . import config
from .consts import Colour
from .utils import md_link, utc_from_ts

# superfluous-parens is erroneously picked sometimes when using :=?
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
            fields: A list of pairs of strings, the name and text of each field.
            inline_all: Whether or not to inline all of the fields.

        """
        super().__init__(**kwargs)
        for field in fields:
            self.add_field(name=field[0], value=field[1], inline=inline_all)


def embed_size_ok(embed: discord.Embed) -> bool:
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
        name_length, value_length = len(field.name), len(field.value)
        if name_length > 256 or value_length > 1024:
            return False

        total_len += name_length + value_length

    if total_len > 6000:
        return False

    return True


def create_schedule_embed(launch_info: Dict) -> discord.Embed:
    """Creates an informational (schedule) embed from a dict of launch information.

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

    schedule_embed = EmbedWithFields(
        color=Colour.red_falcon,
        description=launch_info["details"] or "",
        title=f'Launch #{launch_info["flight_number"]} - {launch_info["mission_name"]}',
        fields=fields,
    )

    if (reddit_url := launch_info["links"]["reddit_campaign"]) is not None:
        schedule_embed.description += (
            f' {md_link("Click for r/SpaceX Thread", reddit_url)}.'
        )

    if (patch_url := launch_info["links"]["mission_patch_small"]) is not None:
        schedule_embed.set_thumbnail(url=patch_url)
    elif (rocket_id := launch_info["rocket"]["rocket_id"]) in ROCKET_ID_IMAGES:
        schedule_embed.set_thumbnail(url=ROCKET_ID_IMAGES[rocket_id])

    if flickr_urls := launch_info["links"]["flickr_images"]:
        schedule_embed.set_image(url=random.choice(flickr_urls))  # nosec

    return schedule_embed


def create_launch_embed(launch_info: Dict) -> discord.Embed:
    """Create a launc embed from a dict of launch information.

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

    launch_embed = EmbedWithFields(
        title="{} is launching soon!".format(launch_info["mission_name"]),
        description=embed_desc,
        color=Colour.red_falcon,
        fields=[["Launch date (UTC)", utc_launch_date]],
    )

    if (patch_url := launch_info["links"]["mission_patch_small"]) is not None:
        launch_embed.set_thumbnail(url=patch_url)
    elif (rocket_id := launch_info["rocket"]["rocket_id"]) in ROCKET_ID_IMAGES:
        launch_embed.set_thumbnail(url=ROCKET_ID_IMAGES[rocket_id])

    return launch_embed


def create_info_embed(guild_count: int, subbed_channel_count: int) -> discord.Embed:
    """Creates an info embed.

    Args:
        guild_count: The number of guilds the bot is currently a member of.
        subbed_channel_count: The number of currently subscribed channels.

    Returns:
        A discord.Embed object.

    """
    return EmbedWithFields(
        title="SpaceXLaunchBot Information",
        color=Colour.red_falcon,
        description="A Discord bot for getting news, information, and notifications "
        "about upcoming SpaceX launches",
        fields=[
            ["Guild Count", f"{guild_count}"],
            ["Subscribed Channel Count", f"{subbed_channel_count}"],
            [
                "Links",
                f'{md_link("Github", config.BOT_GITHUB_URL)}, {md_link("Bot Invite", config.BOT_INVITE_URL)}',
            ],
            ["Contact", f"{config.BOT_OWNER_NAME}"],
            [
                "Help",
                f"Use `{config.BOT_COMMAND_PREFIX} help` to get a list of commands",
            ],
        ],
    )


# TODO: Update with new commands from readme.
HELP_EMBED = EmbedWithFields(
    title="SpaceXLaunchBot Commands",
    description=f"Command prefix: `{config.BOT_COMMAND_PREFIX}`",
    color=Colour.red_falcon,
    inline_all=False,
    fields=[
        [
            "nextlaunch",
            "Send the latest launch information message to the current channel",
        ],
        [
            "add [all|schedule|launch] #channel, @user, @role, etc.",
            "Add the current channel to the notification service with the given notification type. If you chose `all` or `launch`, the second part can be a list of roles / channels / users to ping when a launch notification is sent\n*Only admins can use this command*",
        ],
        [
            "remove",
            "Remove the current channel from the notification service\n*Only admins can use this command*",
        ],
        ["info", "Send information about the bot to the current channel"],
        ["help", "List these commands"],
    ],
)

API_ERROR_EMBED = discord.Embed(
    title="Error",
    description=f"An API error occurred, contact {config.BOT_OWNER_NAME}",
    color=Colour.red_error,
)

LEGACY_PREFIX_WARNING_EMBED = discord.Embed(
    title="New Prefix In Use",
    description="You used a command with the old prefix (!), SpaceXLaunchBot has "
    'moved to using "slb" as a prefix, e.g. `slb help`. This warning will be removed '
    "soon.",
    color=Colour.orange_info,
)
