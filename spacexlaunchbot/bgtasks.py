"""BG Task algo (WIP):
Get new embed dict
--> has it changed?
-->--y send all subbed channels updated embed
-->--n n/a
--> do we meet time criteria for launch notifs?
-->--y have we already sent a launch notif for this embed?
-->--y--n send launch notif
-->--y--y n/a
-->--n n/a
--> sleep for ONE_MINUTE?
"""

import logging, asyncio

import config, apis, embedcreators
from redisclient import redis

log = logging.getLogger(__name__)
ONE_MINUTE = 60


async def notificationTask(client):
    await client.wait_until_ready()
    while not client.is_closed():

        # At the end of this method, remove all channels that we can't access anymore
        channels_to_remove = []

        subbed_channel_ids = await redis.smembers("slb.subscribed_channels")
        subbed_channel_ids = (int(cid) for cid in subbed_channel_ids)

        launching_soon_notif_sent, latest_launch_info_embed_dict = (
            await redis.get_notification_task_store()
        )

        next_launch_dict = await apis.spacex.get_next_launch_dict()

        if next_launch_dict != -1:
            new_launch_info_embed = await embedcreators.get_launch_info_embed(
                next_launch_dict
            )
            new_launch_info_embed_dict = new_launch_info_embed.to_dict()

            if new_launch_info_embed_dict != latest_launch_info_embed_dict:
                log.info("Launch info changed, sending notifications")

                # ? launching_soon_notif_sent = "False"
                latest_launch_info_embed_dict = new_launch_info_embed_dict

                # New launch found, send all "subscribed" channels the embed
                for channel_id in subbed_channel_ids:
                    channel = client.get_channel(channel_id)
                    if channel == None:
                        channels_to_remove.append(channel_id)
                    else:
                        await client.safe_send(channel, new_launch_info_embed)

        # TODO: Notifications for "launching soon"

        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
