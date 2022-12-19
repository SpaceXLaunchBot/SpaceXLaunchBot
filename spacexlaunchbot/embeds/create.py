import discord

from .. import config, version
from ..utils import md_link, utc_from_time
from . import colours
from .better_embed import BetterEmbed

_IMAGE_BASE_URL = (
    "https://raw.githubusercontent.com/r-spacex/SpaceXLaunchBot/master/images/logos"
)

# A map of rocket id (in the API) to the image to represent it
_ROCKET_NAME_IMAGES = {
    "Falcon 9": f"{_IMAGE_BASE_URL}/falcon_9.png",
    "Falcon Heavy": f"{_IMAGE_BASE_URL}/falcon_heavy.png",
    "Falcon 1": f"{_IMAGE_BASE_URL}/logo.jpg",
}


def create_schedule_embed(launch_info: dict) -> BetterEmbed:
    """Creates an informational (schedule) embed from a dict of launch information.

    Args:
        launch_info: A dictionary of launch information from apis.spacex.

    Returns:
        A BetterEmbed object.

    """
    # pylint: disable=line-too-long

    # TODO: The "launch" command can request a launch that won't have all the data and
    #  currently will cause errors (e.g. NoneType TypeError as data does not exist).
    launch_date_str = utc_from_time(launch_info["net"])

    fields = [
        [
            "Launch Vehicle",
            f'{launch_info["rocket"]["configuration"]["full_name"]}',
        ],
        [
            "Launch Date (UTC)",
            f"{launch_date_str}",
        ],
        [
            "Launch Status",
            f'{launch_info["status"]["name"]}',
        ],
        ["Launch Site", launch_info["pad"]["name"]],
    ]

    # for core_dict in launch_info["cores"]:
    #     core_info = ""

    #     if core_dict["core"] is not None:
    #         core_info += f'Serial: {core_dict["core"]["serial"]}\n'

    #     core_info += f'Flight: {core_dict["flight"]}'

    #     if core_dict["landing_attempt"] is False:
    #         core_info += "\nLanding: No"
    #     else:
    #         core_info += f'\nLanding: Yes\nLanding Type: {core_dict["landing_type"]}'

    #     if core_dict["landpad"] is not None:
    #         core_info += f'\nLanding Location: {core_dict["landpad"]["name"]}'

    #     fields.append(["Core Info", core_info])

    # Add a field for the payload
    payload_info = "Name: {}\nType: {}\nOrbit: {}"
    fields.append(
        [
            "Payload",
            payload_info.format(
                launch_info["mission"]["name"],
                launch_info["mission"]["type"],
                launch_info["mission"]["orbit"]["name"],
            ),
        ]
    )

    schedule_embed = BetterEmbed(
        color=colours.RED_FALCON,
        description=launch_info["mission"]["description"] or "",
        title=f'Launch #{launch_info["agency_launch_attempt_count"]} - {launch_info["mission"]["name"]}',
        fields=fields,
    )

    # if (reddit_url := launch_info["links"]["reddit"]["campaign"]) is not None:
    #     schedule_embed.description += "\n" + (  # type: ignore
    #         f' {md_link("Click for r/SpaceX Thread", reddit_url)}.'
    #     )

    # if (patch_url := launch_info["links"]["patch"]["small"]) is not None:
    #     schedule_embed.set_thumbnail(url=patch_url)
    if (
        rocket_id := launch_info["rocket"]["configuration"]["name"]
    ) in _ROCKET_NAME_IMAGES:
        schedule_embed.set_thumbnail(url=_ROCKET_NAME_IMAGES[rocket_id])

    # if flickr_urls := launch_info["links"]["flickr"]["original"]:
    #     schedule_embed.set_image(url=random.choice(flickr_urls))

    return schedule_embed


def create_launch_embed(launch_info: dict) -> BetterEmbed:
    """Create a launch embed from a dict of launch information.

    Args:
        launch_info: A dictionary of launch information from apis.spacex.

    Returns:
        A BetterEmbed object.

    """
    embed_desc = ""
    launch_date_str = utc_from_time(launch_info["net"])

    # if (video_url := launch_info["links"]["webcast"]) is not None:
    #     embed_desc += md_link("Livestream", video_url) + "\n"

    # if (reddit_url := launch_info["links"]["reddit"]["launch"]) is not None:
    #     embed_desc += md_link("r/SpaceX Launch Thread", reddit_url) + "\n"

    # if (press_kit_url := launch_info["links"]["presskit"]) is not None:
    #     embed_desc += md_link("Press kit", press_kit_url) + "\n"

    launch_embed = BetterEmbed(
        title=f"{launch_info['name']} is launching soon!",
        description=embed_desc,
        color=colours.RED_FALCON,
        fields=[["Launch date (UTC)", launch_date_str]],
    )

    # if (patch_url := launch_info["links"]["patch"]["small"]) is not None:
    #     launch_embed.set_thumbnail(url=patch_url)
    if (
        rocket_id := launch_info["rocket"]["configuration"]["name"]
    ) in _ROCKET_NAME_IMAGES:
        launch_embed.set_thumbnail(url=_ROCKET_NAME_IMAGES[rocket_id])

    return launch_embed


def create_info_embed(
    guild_count: int, subbed_channel_count: int, latency_ms: float
) -> BetterEmbed:
    """Creates an info embed.

    Args:
        guild_count: The number of guilds the bot is currently a member of.
        subbed_channel_count: The number of currently subscribed channels.
        latency_ms: The latency to Discord in ms.

    Returns:
        A BetterEmbed object.

    """
    # pylint: disable=line-too-long
    embed = BetterEmbed(
        title="SpaceXLaunchBot Information",
        color=colours.RED_FALCON,
        description="A Discord bot for getting news, information, and notifications "
        "about upcoming SpaceX launches",
        fields=[
            ["Guild Count", f"{guild_count}"],
            ["Subscribed Channel Count", f"{subbed_channel_count}"],
            ["Latency to Discord", f"{latency_ms}ms"],
            [
                "Links",
                f'{md_link("Website", config.WEBSITE_URL)}, {md_link("Github", config.BOT_GITHUB_URL)}, {md_link("Bot Invite", config.BOT_INVITE_URL)}, {md_link("Support Server", config.BOT_SUPPORT_SERVER_INVITE)}',
            ],
            ["Contact", f"{config.BOT_OWNER_NAME}"],
            [
                "Help",
                f"Use `{config.BOT_COMMAND_PREFIX} help` to get a list of commands",
            ],
        ],
    )
    embed.set_footer(text=f"Version {version.SHORT_HASH}")
    return embed


def create_interaction_embed(
    desc: str, success: bool = True, colour: discord.Colour = colours.ORANGE_INFO
) -> BetterEmbed:
    """Creates an embed to be sent in response to a command, e.g. `add`.

    Args:
        desc: What happened?
        success: Was the interaction successful?
        colour: The embed colour.

    Returns:
        A BetterEmbed object.

    """
    return BetterEmbed(
        description=("✅" if success else "❌") + f" {desc}",
        color=colour,
    )
