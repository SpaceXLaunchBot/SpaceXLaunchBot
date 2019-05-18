import logging, asyncio
from datetime import datetime, timedelta
from aredis import RedisError

from redisclient import redis
import config, embedcreators
from apis import spacex

log = logging.getLogger(__name__)
ONE_MINUTE = 60
LAUNCHING_SOON_DELTA = timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


async def _send_all(client, to_send, channel_ids, send_mentions=False):
    """Send all channels in channel_ids to_send
    If send_mentions is true, get mentions from redis and send as well
    Returns a set of channels that are invalid --> should be removed
    """
    invalid_ids = set()
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel == None:
            invalid_ids.add(channel_id)
        else:
            await client.safe_send(channel, to_send)
            if send_mentions:
                mentions = await redis.get_guild_mentions(channel.guild.id)
                if mentions:
                    await client.safe_send(channel, mentions)
    return invalid_ids


async def _check_and_send_notifs(client):
    """Checks what notification messages need to be sent, and send them
    Also updates Redis values if necesseary
    """
    next_launch_dict = await spacex.get_next_launch_dict()

    # If the API is misbehaving, don't do anything, as we risk sending incorrect data
    if next_launch_dict == -1:
        return

    # At the end of this method, remove all channels that we can't access anymore
    channels_to_remove = set()

    subbed_channel_ids = await redis.smembers("slb.subscribed_channels")
    subbed_channel_ids = tuple(int(cid) for cid in subbed_channel_ids)

    # Names shortened to save space, ls = launching soon, li = launch information
    ls_notif_sent, li_embed_dict = await redis.get_notification_task_store()

    new_li_embed = await embedcreators.get_launch_info_embed(next_launch_dict)
    new_li_embed_dict = new_li_embed.to_dict()

    # Send out a launch information embed if it has changed from the previous one
    if new_li_embed_dict != li_embed_dict:
        log.info("Launch info changed, sending notifications")

        ls_notif_sent = "False"
        li_embed_dict = new_li_embed_dict

        # New launch found, send all "subscribed" channels the embed
        invalid_channels = await _send_all(client, new_li_embed, subbed_channel_ids)
        channels_to_remove |= invalid_channels

    try:
        launch_timestamp = int(next_launch_dict["launch_date_unix"])
    except ValueError:
        # Doesen't have a date, don't trigger notifications
        launch_timestamp = 0

    current_time = datetime.utcnow()
    curr_time_plus_delta = (current_time + LAUNCHING_SOON_DELTA).timestamp()

    # Send out a launching soon notification if these criteria are met:
    # If the launch time is within the next NOTIF_TASK_LAUNCH_DELTA, and if the
    # launch_timestamp is not in the past, and we haven't already sent the notif
    if (
        curr_time_plus_delta >= launch_timestamp
        and launch_timestamp >= current_time.timestamp()
        and ls_notif_sent == "False"
    ):
        log.info("Launch is soon, sending out notifications")
        launching_soon_embed = embedcreators.get_launching_soon_embed(next_launch_dict)
        invalid_channels = await _send_all(
            client, launching_soon_embed, subbed_channel_ids, True
        )
        channels_to_remove |= invalid_channels
        ls_notif_sent = True

    # Save any changed data to redis
    await redis.setNotificationTaskStore(ls_notif_sent, li_embed_dict)
    for channel_id in channels_to_remove:
        log.info(f"{channel_id} is an invalid channel ID, removing")
        await redis.srem("slb.subscribed_channels", str(channel_id).encode("UTF-8"))


async def notification_task(client):
    """An async task to send out launching soon & launch info notifications
    """
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            await _check_and_send_notifs(client)
        except RedisError as e:
            # TODO: Does this log variable work for both functions (distinguishable?)
            log.error(f"RedisError occurred: {e}")

        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
