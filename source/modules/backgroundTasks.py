"""
Async tasks to run in the background
"""

import asyncio
import logging
from datetime import datetime, timedelta

from modules.redisClient import redisConn
from modules import embedGenerators, structure, apis

logger = logging.getLogger(__name__)

ONE_MINUTE = 60  # Just makes things a little more readable
API_CHECK_INTERVAL = structure.config["apiCheckInterval"]
LAUNCH_NOTIF_DELTA = timedelta(minutes = structure.config["launchNotificationDelta"])

async def notificationTask(client):
    """
    Every API_CHECK_INTERVAL minutes:
    If the embed has changed, something new has happened so send
        all channels an embed with updated info
    If the time of the next upcoming launch is within the next hour,
        send out a notification embed alerting people
    """
    await client.wait_until_ready()
    logger.info("Started")
    while not client.is_closed():
        """
        Getting everything and then checking for errors probably isn't very
        efficient but since this is run on a set time loop and runs in the
        background, it shouldn't matter much...
        """

        channelsToRemove = []
        nextLaunchJSON = await apis.spacexAPI.getNextLaunchJSON()
        
        if nextLaunchJSON == -1:
            # Can't do anything if API isn't working, skip this cycle
            pass
        
        elif not await redisConn.exists("subscribedChannels"):
            # No subscribedChannels SET, no channels to send notifications to
            pass

        else:
            subbedChannelIDs = await redisConn.smembers("subscribedChannels")
            # Redis returns strings from a set, we want integers
            subbedChannelIDs = [int(cid) for cid in subbedChannelIDs]

            notificationTaskStore = await redisConn.getNotificationTaskStore()
            launchingSoonNotifSent = notificationTaskStore["launchingSoonNotifSent"]
            latestLaunchInfoEmbedDict = notificationTaskStore["latestLaunchInfoEmbedDict"]
            
            launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            launchInfoEmbedDict = launchInfoEmbed.to_dict()  # Only calculate this once

            # Launch information message
            if latestLaunchInfoEmbedDict == launchInfoEmbedDict:
                pass
            else:
                logger.info("Launch info changed, sending notifications")

                launchingSoonNotifSent = "False"
                latestLaunchInfoEmbedDict = launchInfoEmbedDict

                # New launch found, send all "subscribed" channels the embed
                for channelID in subbedChannelIDs:
                    channel = client.get_channel(channelID)
                    if channel == None:
                        channelsToRemove.append(channelID)
                    else:
                        await client.safeSendLaunchInfo(channel, [launchInfoEmbed, launchInfoEmbedLite])

            # Launch notification message
            launchTime = nextLaunchJSON["launch_date_unix"]
            if await structure.isInt(launchTime):
                
                launchTime = int(launchTime)

                # Get timestamp for the time LAUNCH_NOTIF_DELTA from now
                currentTime = datetime.utcnow()
                timePlusDelta = (currentTime + LAUNCH_NOTIF_DELTA).timestamp()

                # If the launch time is within the next LAUNCH_NOTIF_DELTA
                # and if the launchTime is not in the past
                if timePlusDelta >= launchTime and launchTime >= currentTime.timestamp():
                    if launchingSoonNotifSent == "False":

                        logger.info(f"Launch happening within {LAUNCH_NOTIF_DELTA}, sending notification")
                        launchingSoonNotifSent = "True"
                        launchingSoonEmbed = await embedGenerators.getLaunchingSoonEmbed(nextLaunchJSON)
                        
                        for channelID in subbedChannelIDs:
                            channel = client.get_channel(channelID)
                            if channel == None:
                                channelsToRemove.append(channelID)
                            else:
                                await client.safeSend(channel, launchingSoonEmbed)
                                guildSettings = await redisConn.getGuildSettings(channel.guild.id)         

                                # TODO: Deal with database error (-1) differently?
                                if guildSettings != 0 and guildSettings != -1:
                                    # Ping the roles/users (mentions) requested
                                    await client.safeSend(channel, guildSettings["rolesToMention"])
                            
                    else:
                        logger.info(f"Launch happening within {LAUNCH_NOTIF_DELTA}, launchingSoonNotifSent is {launchingSoonNotifSent}")
                        
            # Save any changed data to redis
            # Remove channels that we can't access anymore
            for channelID in channelsToRemove:
                logger.info(f"{channelID} is not a valid channel ID, removing")
                await redisConn.srem("subscribedChannels", str(channelID))
            # Error checking happens inside the function
            await redisConn.setNotificationTaskStore(launchingSoonNotifSent, latestLaunchInfoEmbedDict)

        await asyncio.sleep(ONE_MINUTE * API_CHECK_INTERVAL)
