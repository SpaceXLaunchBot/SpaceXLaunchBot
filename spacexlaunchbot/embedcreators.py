import copy, discord
from structure import utc_from_ts
from statics import falcon_red, rocket_id_images, general_error_embed, owner_mention

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
    if next_launch_dict["details"] == None:
        next_launch_dict["details"] = ""

    launch_info_embed = discord.Embed(
        color=falcon_red,
        description=next_launch_dict["details"],
        title="Launch #{} - {}".format(
            next_launch_dict["flight_number"], next_launch_dict["mission_name"]
        ),
    )

    # Set thumbnail depending on rocket ID
    if next_launch_dict["rocket"]["rocket_id"] in rocket_id_images:
        launch_info_embed.set_thumbnail(
            url=rocket_id_images[next_launch_dict["rocket"]["rocket_id"]]
        )

    launch_info_embed.add_field(
        name="Launch vehicle",
        value="{} {}".format(
            next_launch_dict["rocket"]["rocket_name"],
            next_launch_dict["rocket"]["rocket_type"],
        ),
    )

    # Add a field for the launch date
    UTCLaunchDate = await utc_from_ts(next_launch_dict["launch_date_unix"])
    launch_info_embed.add_field(
        name="Launch date",
        value=launch_date_info.format(
            UTCLaunchDate, next_launch_dict["tentative_max_precision"]
        ),
    )

    # Basic embed structure built, copy into small version
    launch_info_embed_small = copy.deepcopy(launch_info_embed)

    discussion_url = next_launch_dict["links"]["reddit_campaign"]
    if discussion_url != None:
        launch_info_embed.add_field(name="r/SpaceX discussion", value=discussion_url)

    launch_info_embed.add_field(
        name="Launch site", value=next_launch_dict["launch_site"]["site_name_long"]
    )

    if next_launch_dict["rocket"]["rocket_id"] == "falcon9":
        # TODO: Allow "Core Info" section for FH
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
        return general_error_embed
    elif len(launch_info_embed) > 2048:
        # If body is too big, send small embed
        return launch_info_embed_small
    return launch_info_embed


async def get_launching_soon_embed(next_launch_dict):
    embed_desc = ""

    notif_embed = discord.Embed(
        color=falcon_red,
        title="{} is launching soon!".format(next_launch_dict["mission_name"]),
    )

    if next_launch_dict["links"]["mission_patch_small"] != None:
        notif_embed.set_thumbnail(url=next_launch_dict["links"]["mission_patch_small"])
    elif next_launch_dict["rocket"]["rocket_id"] in rocket_id_images:
        notif_embed.set_thumbnail(
            url=rocket_id_images[next_launch_dict["rocket"]["rocket_id"]]
        )

    # discord.Embed links [using](markdown)
    if next_launch_dict["links"]["video_link"] != None:
        embed_desc += f"[Livestream]({next_launch_dict['links']['video_link']})\n"
    if next_launch_dict["links"]["reddit_launch"] != None:
        embed_desc += (
            f"[r/SpaceX Launch Thread]({next_launch_dict['links']['reddit_launch']})\n"
        )
    if next_launch_dict["links"]["presskit"] != None:
        embed_desc += f"[Press kit]({next_launch_dict['links']['presskit']})\n"
    notif_embed.description = embed_desc

    UTCLaunchDate = await utc_from_ts(next_launch_dict["launch_date_unix"])
    notif_embed.add_field(name="Launch date", value=UTCLaunchDate)

    return notif_embed


async def get_info_embed():
    """Info ideas:
    - Developer / Owner tag
    - Guild, Channel, and User count
    - Uptime
    - Github link
    - Invite link
    - Bot metrics (command count, avg commands per ?, etc.)
    - API latency?
    - Let user know about !help
    """
    info_embed = discord.Embed(
        title="SpaceXLaunchBot Information",
        color=falcon_red,
        description="A Discord bot for getting news, information, and notifications about upcoming SpaceX launches",
    )
    info_embed.add_field(
        name="Links", value="[GitHub](https://github.com/r-spacex/SpaceXLaunchBot)"
    )
    info_embed.add_field(name="Contact", value=f"{owner_mention}")
    info_embed.add_field(
        name="Help", value="Use the command !help to get a list of commands"
    )
    return info_embed
