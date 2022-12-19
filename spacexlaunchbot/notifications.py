import datetime
import logging
from enum import Enum

from . import config, embeds
from .apis import ll2

_LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


class NotificationType(Enum):
    """Represents each type of notification."""

    # NOTE: Changing these to uppercase will require changing the enum in the db :/
    # pylint: disable=invalid-name

    all = 0
    schedule = 1
    launch = 2


async def check_and_send_notifications(client) -> None:
    """Checks what notification messages need to be sent, and sends them.

    Updates database values if they need updating.

    Args:
        client: The Discord client to use to send messages.

    """
    next_launch_dict = await ll2.get_launch_dict()
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

    before_flight = not next_launch_dict["status"]["name"] in [
        "Launch in Flight",
        "Launch Successful",
    ]

    if before_flight and diff_str != "":
        logging.info(f"Sending notifications for launch schedule, diff: {diff_str}")
        schedule_embed.set_footer(text=diff_str)
        await client.send_notification(schedule_embed, NotificationType.schedule)
        launch_embed_for_current_schedule_sent = False

    #
    # Launch Notification
    #

    try:
        # launch_timestamp = int(next_launch_dict["date_unix"])
        launch_timestamp = int(
            datetime.datetime.fromisoformat(next_launch_dict["net"]).timestamp()
        )

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
        and next_launch_dict["status"]["id"] == 1  # 1 is "Go for Launch"
    ):
        logging.info(f"Sending notifications for launch @ timestamp {launch_timestamp}")
        launch_embed_for_current_schedule_sent = True
        launch_embed = embeds.create_launch_embed(next_launch_dict)
        await client.send_notification(launch_embed, NotificationType.launch)

    #
    # Save data
    #

    client.ds.set_notification_task_vars(
        launch_embed_for_current_schedule_sent, schedule_embed.to_dict()
    )
