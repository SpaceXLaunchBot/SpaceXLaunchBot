import logging
import asyncio
import datetime
import aredis

import config
import embedcreators
import apis
from redisclient import redis

ONE_MINUTE = 60
LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


async def _check_and_send_notifs(client):
    """Checks what notification messages need to be sent, and send them
    Updates Redis values if necessary
    """
    next_launch_dict = await apis.spacex.get_next_launch_dict()

    # If the API is misbehaving, don't do anything, as we risk sending incorrect data
    if next_launch_dict == -1:
        return

    # At the end of this method, remove all channels that we can't access anymore
    channels_to_remove = set()

    # Names shortened to save space, ls = launching soon, li = launch information
    ls_notif_sent, li_embed_dict = await redis.get_notification_task_store()

    new_li_embed = await embedcreators.get_launch_info_embed(next_launch_dict)
    new_li_embed_dict = new_li_embed.to_dict()

    # Send out a launch information embed if it has changed from the previous one
    if new_li_embed_dict != li_embed_dict:
        logging.info("Launch info changed, sending notifications")

        ls_notif_sent = "False"
        li_embed_dict = new_li_embed_dict

        # New launch found, send all "subscribed" channels the embed
        invalid_channels = await client.send_all_subscribed(new_li_embed)
        channels_to_remove |= invalid_channels

    try:
        launch_timestamp = int(next_launch_dict["launch_date_unix"])
    except ValueError:
        # Doesn't have a date, don't trigger notifications
        launch_timestamp = 0

    current_time = datetime.datetime.utcnow()
    curr_time_plus_delta = (current_time + LAUNCHING_SOON_DELTA).timestamp()

    # Send out a launching soon notification if these criteria are met:
    # If the launch time is within the next NOTIF_TASK_LAUNCH_DELTA, and if the
    # launch_timestamp is not in the past, and we haven't already sent the notif
    if (
        curr_time_plus_delta >= launch_timestamp >= current_time.timestamp()
        and ls_notif_sent == "False"
    ):
        logging.info("Launch is soon, sending out notifications")
        launching_soon_embed = await embedcreators.get_launching_soon_embed(
            next_launch_dict
        )
        invalid_channels = await client.send_all_subscribed(launching_soon_embed, True)
        channels_to_remove |= invalid_channels
        ls_notif_sent = "True"

    # Save any changed data to redis
    await redis.set_notification_task_store(ls_notif_sent, li_embed_dict)
    for channel_id in channels_to_remove:
        logging.info(f"{channel_id} is an invalid channel ID, removing")
        await redis.remove_subbed_channel(channel_id)


async def notification_task(client):
    """An async task to send out launching soon & launch info notifications
    """
    await client.wait_until_ready()
    logging.info("Starting")

    while not client.is_closed():
        try:
            await _check_and_send_notifs(client)

        except aredis.RedisError as ex:
            logging.error(f"RedisError occurred: {type(ex).__name__}: {ex}")

        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
