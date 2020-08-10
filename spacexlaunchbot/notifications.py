import asyncio
import datetime
import logging
from enum import Enum

import discord

from . import apis
from . import config

ONE_MINUTE = 60
LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


# TODO: https://stackoverflow.com/a/41409392/6396652
class NotificationType(Enum):
    all = 0
    schedule = 1
    launch = 2


async def _check_and_send_notifs(client: discord.Client) -> None:
    """Checks what notification messages need to be sent, and sends them.

    Updates database values if they need updating.

    Args:
        client: The Discord client to use to send messages.

    """
    next_launch_dict = await apis.spacex.get_launch_dict()
    if next_launch_dict == {}:
        return

    (
        current_schedule_notification_sent,
        previous_schedule_embed_dict,
    ) = client.ds.get_notification_task_vars()

    # TODO:

    # Schedule Notification
    pass

    # Launch Notification
    pass


async def notification_task(client: discord.Client) -> None:
    """An async task to send out launching soon & launch info notifications."""
    logging.info("Waiting for client ready")
    await client.wait_until_ready()
    logging.info("Starting")

    while not client.is_closed():
        await _check_and_send_notifs(client)
        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
