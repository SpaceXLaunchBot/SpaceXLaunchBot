import asyncio
import datetime
import logging

from . import config
from . import embeds
from .apis import spacex
from .consts import NotificationType

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
        launch_embed_for_current_schedule_sent,
        previous_schedule_embed_dict,
    ) = client.ds.get_notification_task_vars()

    #
    # Schedule Notification
    #

    schedule_embed = embeds.create_schedule_embed(next_launch_dict)
    if schedule_embed.to_dict() != previous_schedule_embed_dict:
        # TODO: Write to footer what changes occurred.
        client.send_notification(schedule_embed, NotificationType.schedule)
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
    current_time_plus_delta = (current_time + LAUNCHING_SOON_DELTA).timestamp()

    # If the launch time is within the next NOTIF_TASK_LAUNCH_DELTA, and if the
    # launch_timestamp is not in the past, and we haven't already sent the notif.
    if (
        current_time_plus_delta >= launch_timestamp >= current_time.timestamp()
        and launch_embed_for_current_schedule_sent is False
    ):
        launch_embed_for_current_schedule_sent = True
        launch_embed = embeds.create_launch_embed(next_launch_dict)
        client.send_notification(launch_embed, NotificationType.launch)

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
        await _check_and_send_notifs(client)
        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
