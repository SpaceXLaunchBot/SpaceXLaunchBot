import logging
import asyncio
import datetime
import aredis
import hashlib
import json
import discord
from typing import Set

import discordclient  # pylint: disable=unused-import
import config
import embedcreators
import apis
from redisclient import redis

ONE_MINUTE = 60
LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


async def hash_embed(embed: discord.Embed) -> str:
    """
    Takes an Embed obj, converts to a sorted JSON string and returns the SHA256 hash

    :param embed: A discord.Embed object
    :return: A string containing the hexadecimal digits of the hash
    """
    # sort_keys ensures consistency
    sorted_embed_dict = json.dumps(embed.to_dict(), sort_keys=True)
    sorted_embed_dict_bytes = sorted_embed_dict.encode("UTF-8")
    return hashlib.sha256(sorted_embed_dict_bytes).hexdigest()


async def _check_and_send_notifs(client: "discordclient.SpaceXLaunchBotClient") -> None:
    """
    Checks what notification messages need to be sent, and sends them
    Updates Redis values if they need updating

    :param client: A discord.Client object
    :return: None
    """
    next_launch_dict = await apis.spacex.get_launch_dict()

    # If the API is misbehaving, don't do anything, don't risk sending incorrect data
    if next_launch_dict == {}:
        return

    # At the end of this method, remove all channels that can't be access anymore
    channels_to_remove: Set[int] = set()

    # Shortened to save space, ls = launching soon, li = launch information
    ls_notif_sent, latest_li_embed_hash = await redis.get_notification_task_store()

    new_li_embed = await embedcreators.get_launch_info_embed(next_launch_dict)
    new_li_embed_hash = await hash_embed(new_li_embed)

    # Send out a launch information embed if it has changed from the previous one
    if new_li_embed_hash != latest_li_embed_hash:
        logging.info("Launch info changed, sending notifications")

        ls_notif_sent = "False"
        latest_li_embed_hash = new_li_embed_hash

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
    await redis.set_notification_task_store(ls_notif_sent, latest_li_embed_hash)
    await redis.remove_subbed_channels(channels_to_remove)


async def notification_task(client: "discordclient.SpaceXLaunchBotClient") -> None:
    """
    An async task to send out launching soon & launch info notifications

    :param client: A discord.Client object
    :return: None
    """
    await client.wait_until_ready()
    logging.info("Starting")

    while not client.is_closed():
        try:
            await _check_and_send_notifs(client)

        except aredis.RedisError as ex:
            logging.error(f"RedisError occurred: {type(ex).__name__}: {ex}")

        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
