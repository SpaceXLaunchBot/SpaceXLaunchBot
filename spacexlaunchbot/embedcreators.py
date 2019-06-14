import copy, discord
import config, structure, statics
from redisclient import redis

payload_info = """Type: {}
Orbit: {}
Mass: {}
Manufacturer: {}
Customer{}: {}
"""
core_info = """Serial: {}
Flight: {}
Landing: {}
Landing Type: {}
Landing Vehicle: {}
"""
launch_date_info = """{}
Precision: {}
"""


async def get_launch_info_embed(next_launch_dict):

    # Having desc set to `None` breaks things
    if next_launch_dict["details"] is None:
        next_launch_dict["details"] = ""

    launch_info_embed = discord.Embed(
        color=statics.falcon_red,
        description=next_launch_dict["details"],
        title="Launch #{} - {}".format(
            next_launch_dict["flight_number"], next_launch_dict["mission_name"]
        ),
    )

    # Set thumbnail depending on rocket ID, use mission patch if available
    if next_launch_dict["links"]["mission_patch_small"] is not None:
        launch_info_embed.set_thumbnail(
            url=next_launch_dict["links"]["mission_patch_small"]
        )
    elif next_launch_dict["rocket"]["rocket_id"] in statics.rocket_id_images:
        launch_info_embed.set_thumbnail(
            url=statics.rocket_id_images[next_launch_dict["rocket"]["rocket_id"]]
        )

    launch_info_embed.add_field(
        name="Launch vehicle",
        value="{} {}".format(
            next_launch_dict["rocket"]["rocket_name"],
            next_launch_dict["rocket"]["rocket_type"],
        ),
    )

    # Add a field for the launch date
    utc_launch_date = await structure.utc_from_ts(next_launch_dict["launch_date_unix"])
    launch_info_embed.add_field(
        name="Launch date",
        value=launch_date_info.format(
            utc_launch_date, next_launch_dict["tentative_max_precision"]
        ),
    )

    # Basic embed structure built, copy into small version
    launch_info_embed_small = copy.deepcopy(launch_info_embed)

    discussion_url = next_launch_dict["links"]["reddit_campaign"]
    if discussion_url is not None:
        launch_info_embed.add_field(name="r/SpaceX discussion", value=discussion_url)

    launch_info_embed.add_field(
        name="Launch site", value=next_launch_dict["launch_site"]["site_name_long"]
    )

    if next_launch_dict["rocket"]["rocket_id"] == "falcon9":
        # Falcon 9 always has 1 core, FH (or others) will be different
        launch_info_embed.add_field(
            name="Core info",
            value=core_info.format(
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["core_serial"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["flight"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["landing_intent"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0]["landing_type"],
                next_launch_dict["rocket"]["first_stage"]["cores"][0][
                    "landing_vehicle"
                ],
            ),
        )

    elif next_launch_dict["rocket"]["rocket_id"] == "falconheavy":
        for core_num, core_dict in enumerate(
            next_launch_dict["rocket"]["first_stage"]["cores"]
        ):
            launch_info_embed.add_field(
                name=f"Core {core_num} info",
                value=core_info.format(
                    core_dict["core_serial"],
                    core_dict["flight"],
                    core_dict["landing_intent"],
                    core_dict["landing_type"],
                    core_dict["landing_vehicle"],
                ),
            )

    # Add a field for each payload, with basic information
    for payload in next_launch_dict["rocket"]["second_stage"]["payloads"]:
        launch_info_embed.add_field(
            name="Payload: {}".format(payload["payload_id"]),
            value=payload_info.format(
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
        return statics.general_error_embed
    elif len(launch_info_embed) > 2048:
        # If body is too big, send small embed
        return launch_info_embed_small
    return launch_info_embed


async def get_launching_soon_embed(next_launch_dict):
    embed_desc = ""

    notif_embed = discord.Embed(
        color=statics.falcon_red,
        title="{} is launching soon!".format(next_launch_dict["mission_name"]),
    )

    if next_launch_dict["links"]["mission_patch_small"] is not None:
        notif_embed.set_thumbnail(url=next_launch_dict["links"]["mission_patch_small"])
    elif next_launch_dict["rocket"]["rocket_id"] in statics.rocket_id_images:
        notif_embed.set_thumbnail(
            url=statics.rocket_id_images[next_launch_dict["rocket"]["rocket_id"]]
        )

    # Embed links [using](markdown)
    if next_launch_dict["links"]["video_link"] is not None:
        embed_desc += f"[Livestream]({next_launch_dict['links']['video_link']})\n"
    if next_launch_dict["links"]["reddit_launch"] is not None:
        embed_desc += (
            f"[r/SpaceX Launch Thread]({next_launch_dict['links']['reddit_launch']})\n"
        )
    if next_launch_dict["links"]["presskit"] is not None:
        embed_desc += f"[Press kit]({next_launch_dict['links']['presskit']})\n"
    notif_embed.description = embed_desc

    utc_launch_date = await structure.utc_from_ts(next_launch_dict["launch_date_unix"])
    notif_embed.add_field(name="Launch date", value=utc_launch_date)

    return notif_embed


async def get_info_embed(client):
    guild_count = len(client.guilds)
    subbed_channel_count = await redis.subbed_channels_count()

    info_embed = discord.Embed(
        title="SpaceXLaunchBot Information",
        color=statics.falcon_red,
        description="A Discord bot for getting news, information, and notifications about upcoming SpaceX launches",
    )

    info_embed.add_field(name="Guild Count", value=f"{guild_count}")
    info_embed.add_field(
        name="Subscribed Channel Count", value=f"{subbed_channel_count}"
    )
    info_embed.add_field(
        name="Links",
        value=f"[GitHub]({config.BOT_GITHUB}), [Bot Invite]({config.BOT_INVITE})",
    )
    info_embed.add_field(name="Contact", value=f"{statics.owner_mention}")
    info_embed.add_field(
        name="Help", value="Use the command !help to get a list of commands"
    )

    return info_embed
