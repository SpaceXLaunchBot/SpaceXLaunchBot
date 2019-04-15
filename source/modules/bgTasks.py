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
from modules.redisClient import redisConn


logger = logging.getLogger(__name__)

ONE_MINUTE = 60


async def notificationTask(client):
    await client.wait_until_ready()
    while not client.is_closed():

        # At the end of this method, remove all channels that we can't access anymore
        channelsToRemove = []

        nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON()

        if nextLaunchJSON != -1:

            launchInfoEmbed = await embedGenerators.genLaunchInfoEmbeds(nextLaunchJSON)
            launchInfoEmbedDict = launchInfoEmbed.to_dict()

            subbedChannelIDs = await redisConn.smembers("subscribedChannels")
            subbedChannelIDs = (int(cid) for cid in subbedChannelIDs)

            notifTaskStore = await redisConn.getNotificationTaskStore()
            launchingSoonNotifSent = notifTaskStore["launchingSoonNotifSent"]
            latestLaunchInfoEmbedDict = notifTaskStore["latestLaunchInfoEmbedDict"]

            if launchInfoEmbedDict != latestLaunchInfoEmbedDict:
                logger.info("Launch info changed, sending notifications")

                launchingSoonNotifSent = "False"
                latestLaunchInfoEmbedDict = launchInfoEmbedDict

                # New launch found, send all "subscribed" channels the embed
                for channelID in subbedChannelIDs:
                    channel = client.get_channel(channelID)
                    if channel == None:
                        channelsToRemove.append(channelID)
                    else:
                        await client.safeSend(channel, launchInfoEmbed)

        # TODO: Notifications for "launching soon"

        await asyncio.sleep(ONE_MINUTE * config.API_CHECK_INTERVAL)
