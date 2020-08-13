import asyncio
import datetime
import logging
from enum import Enum

from . import config
from . import embeds
from .apis import spacex

_ONE_MINUTE = 60
_LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


class NotificationType(Enum):
    """Represents each type of notification."""

    all = 0
    schedule = 1
    launch = 2


async def _check_and_send_notifications(client) -> None:
    """Checks what notification messages need to be sent, and sends them.

    Updates database values if they need updating.

    Args:
        client: The Discord client to use to send messages.

    """
    next_launch_dict = await spacex.get_launch_dict()
    if next_launch_dict == {}:
        return

    (
        launch_embed_for_current_schedule_sent,
        previous_schedule_embed_dict,
    ) = client.ds.get_notification_task_vars()

    #
    # Schedule Notification
    #

    schedule_embed = embeds.create_schedule_embed(next_launch_dict)
    diff_str = embeds.diff_schedule_embed_dicts(
        previous_schedule_embed_dict, schedule_embed.to_dict()
    )

    if diff_str != "":
        schedule_embed.set_footer(text=diff_str)
        await client.send_notification(schedule_embed, NotificationType.schedule)
        launch_embed_for_current_schedule_sent = False

    #
    # Launch Notification
    #

    try:
        launch_timestamp = int(next_launch_dict["launch_date_unix"])
    except ValueError:
        # Doesn't have a date, don't trigger notifications
        launch_timestamp = 0

    current_time = datetime.datetime.utcnow()
    current_time_plus_delta = (current_time + _LAUNCHING_SOON_DELTA).timestamp()

    # If the launch time is within the next NOTIF_TASK_LAUNCH_DELTA, and if the
    # launch_timestamp is not in the past, and we haven't already sent the notif,
    # and the launch time precision is at the best.
    if (
        current_time_plus_delta >= launch_timestamp >= current_time.timestamp()
        and launch_embed_for_current_schedule_sent is False
        and next_launch_dict.get("tentative_max_precision", "") == "hour"
    ):
        launch_embed_for_current_schedule_sent = True
        launch_embed = embeds.create_launch_embed(next_launch_dict)
        await client.send_notification(launch_embed, NotificationType.launch)

    #
    # Save data
    #

    client.ds.set_notification_task_vars(
        launch_embed_for_current_schedule_sent, schedule_embed.to_dict()
    )


async def notification_task(client) -> None:
    """An async task to send out launching soon & launch info notifications."""
    logging.info("Waiting for client ready")
    await client.wait_until_ready()
    logging.info("Starting")

    while not client.is_closed():
        await _check_and_send_notifications(client)
        await asyncio.sleep(_ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
