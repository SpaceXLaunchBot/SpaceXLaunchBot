"""
BG Task algo (WIP):
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

import config
from modules import apis, embedGenerators
from modules.redis_client import redis


logger = logging.getLogger(__name__)

ONE_MINUTE = 60


async def notificationTask(client):
    await client.wait_until_ready()
    while not client.is_closed():

        # At the end of this method, remove all channels that we can't access anymore
        channelsToRemove = []

        next_launch_dict = await apis.SpacexApi.get_next_launch_dict()

        if next_launch_dict != -1:

            launch_info_embed = await embedGenerators.gen_launch_info_embeds(
                next_launch_dict
            )
            launch_info_embedDict = launch_info_embed.to_dict()

            subbedChannelIDs = await redis.smembers("subscribedChannels")
            subbedChannelIDs = (int(cid) for cid in subbedChannelIDs)

            notifTaskStore = await redis.getNotificationTaskStore()
            launchingSoonNotifSent = notifTaskStore["launchingSoonNotifSent"]
            latestlaunch_info_embedDict = notifTaskStore["latestlaunch_info_embedDict"]

            if launch_info_embedDict != latestlaunch_info_embedDict:
                logger.info("Launch info changed, sending notifications")

                launchingSoonNotifSent = "False"
                latestlaunch_info_embedDict = launch_info_embedDict

                # New launch found, send all "subscribed" channels the embed
                for channelID in subbedChannelIDs:
                    channel = client.get_channel(channelID)
                    if channel == None:
                        channelsToRemove.append(channelID)
                    else:
                        await client.safe_send(channel, launch_info_embed)

        # TODO: Notifications for "launching soon"

        await asyncio.sleep(ONE_MINUTE * config.API_CHECK_INTERVAL)
