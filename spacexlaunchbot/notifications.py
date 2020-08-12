import asyncio
import datetime
import logging

from . import config
from .apis import spacex

ONE_MINUTE = 60
LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


async def _check_and_send_notifs(client) -> None:
    """Checks what notification messages need to be sent, and sends them.

    Updates database values if they need updating.

    Args:
        client: The Discord client to use to send messages.

    """
    next_launch_dict = await spacex.get_launch_dict()
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


async def notification_task(client) -> None:
    """An async task to send out launching soon & launch info notifications."""
    logging.info("Waiting for client ready")
    await client.wait_until_ready()
    logging.info("Starting")

    while not client.is_closed():
        await _check_and_send_notifs(client)
        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
