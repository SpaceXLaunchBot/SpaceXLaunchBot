import logging

from .. import apis, embeds
from ..notifications import NotificationType
from .helpers import _req_id_owner, _req_perm_admin


async def next_launch(**kwargs):
    next_launch_dict = await apis.spacex.get_launch_dict()
    if next_launch_dict == {}:
        return embeds.API_ERROR_EMBED
    return embeds.create_schedule_embed(next_launch_dict)


async def launch(**kwargs):
    operands = kwargs["operands"]

    try:
        launch_number = int(operands[0])
    except ValueError:
        return embeds.create_interaction_embed("Invalid launch number", success=False)

    launch_dict = await apis.spacex.get_launch_dict(launch_number)
    if launch_dict == {}:
        return embeds.API_ERROR_EMBED
    return embeds.create_schedule_embed(launch_dict)


@_req_perm_admin
async def add(**kwargs):
    client, message, operands = kwargs["client"], kwargs["message"], kwargs["operands"]
    notif_type_str, notif_mentions = operands[0], operands[1:]

    try:
        notif_type = NotificationType[notif_type_str]
    except KeyError:
        return embeds.create_interaction_embed(
            "Invalid notification type", success=False
        )

    notif_mentions_str = " ".join(notif_mentions)

    added = await client.ds.add_subbed_channel(
        str(message.channel.id),
        message.channel.name,
        str(message.guild.id),
        notif_type,
        notif_mentions_str,
    )
    if added is False:
        return embeds.create_interaction_embed(
            "This channel is already subscribed to the notification service",
            success=False,
        )
    logging.info(f"{message.channel.id} subscribed to {notif_type_str}")
    return embeds.create_interaction_embed(
        "This channel has been added to the notification service"
    )


@_req_perm_admin
async def remove(**kwargs):
    client, message = kwargs["client"], kwargs["message"]
    cid = str(message.channel.id)
    if await client.ds.remove_subbed_channel(cid) is False:
        return embeds.create_interaction_embed(
            "This channel was not previously subscribed to the notification service",
            success=False,
        )
    logging.info(f"{message.channel.id} unsubscribed")
    return embeds.create_interaction_embed(
        "This channel has been removed from the notification service"
    )


async def info(**kwargs):
    client = kwargs["client"]
    guild_count = len(client.guilds)
    channel_count = await client.ds.subbed_channels_count()
    return embeds.create_info_embed(guild_count, channel_count, client.latency_ms)


async def help_cmd(**kwargs):
    # Appended with _cmd as to not overwrite built-in `help`.
    return embeds.HELP_EMBED


@_req_id_owner
async def debug_launch_embed(**kwargs):
    """Send a launch notification embed for the given launch."""
    operands = kwargs["operands"]

    try:
        launch_number = int(operands[0])
    except ValueError:
        return embeds.create_interaction_embed("Invalid launch number", success=False)

    launch_dict = await apis.spacex.get_launch_dict(launch_number)
    if launch_dict == {}:
        return "API returned `{}`"
    return embeds.create_launch_embed(launch_dict)


@_req_id_owner
async def reset_notification_task_store(**kwargs):
    """Reset notification_task_store to default (will trigger new notifications)."""
    logging.warning("reset notification task store command called")
    client = kwargs["client"]
    client.ds.set_notification_task_vars(False, {})
    return "Reset using `set_notification_task_vars(False, {})`"


@_req_id_owner
async def shutdown(**kwargs):
    logging.info("shutdown command called")
    client = kwargs["client"]
    await client.shutdown()
