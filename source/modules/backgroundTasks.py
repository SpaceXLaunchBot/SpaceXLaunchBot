"""
Async tasks to run in the background
"""

from datetime import datetime, timedelta
import asyncio
import logging

from redisClient import redisConn

from modules import embedGenerators, spacexAPI, utils, fs
from modules.discordUtils import safeSend, safeSendLaunchInfo

logger = logging.getLogger(__name__)

ONE_MINUTE = 60  # Just makes things a little more readable
API_CHECK_INTERVAL = fs.config["apiCheckInterval"]
LAUNCH_NOTIF_DELTA = timedelta(minutes = fs.config["launchNotificationDelta"])
REAPER_INTERVAL = fs.config["reaperInterval"]

async def notificationTask(client):
    """
    Every $API_CHECK_INTERVAL minutes:
    If the embed has changed, something new has happened so send
        all channels an embed with updated info
    If the time of the next upcoming launch is within the next hour,
        send out a notification embed alerting people
    """
    await client.wait_until_ready()
    logger.info("Started")
    while not client.is_closed:
        
        # Gather latest data from redis
        subbedChannelIDs = await redisConn.get("subscribedChannels", obj=True)
        # launchNotifSent is a string so it can be saved to and loaded from Redis easily
        launchNotifSent = await redisConn.get("launchNotifSent")
        latestLaunchInfoEmbedDict = await redisConn.get("latestLaunchInfoEmbedDict", obj=True)

        nextLaunchJSON = await spacexAPI.getNextLaunchJSON()
        if nextLaunchJSON == 0:
            logger.error("nextLaunchJSON returned 0, skipping this cycle")
            pass  # Error, wait for next loop/cycle
        
        else:
            launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            launchInfoEmbedDict = launchInfoEmbed.to_dict()  # Only calculate this once

            if latestLaunchInfoEmbedDict == launchInfoEmbedDict:
                pass
            else:
                logger.info("Launch info changed, sending notifications")

                launchNotifSent = "False"
                latestLaunchInfoEmbedDict = launchInfoEmbedDict

                # new launch found, send all "subscribed" channel the embed
                for channelID in subbedChannelIDs:
                    channel = client.get_channel(channelID)
                    await safeSendLaunchInfo(client, channel, [launchInfoEmbed, launchInfoEmbedLite])

            launchTime = nextLaunchJSON["launch_date_unix"]
            if await utils.isInt(launchTime):
                
                launchTime = int(launchTime)

                # Get timestamp for the time $LAUNCH_NOTIF_DELTA minutes from now
                nextHour = (datetime.utcnow() + LAUNCH_NOTIF_DELTA).timestamp()

                # If the launch time is within the next hour
                if nextHour > launchTime:
                    if launchNotifSent == "False":

                        logger.info(f"Launch happening within {LAUNCH_NOTIF_DELTA} minutes, sending notification")
                        launchNotifSent = "True"

                        notifEmbed = await embedGenerators.getLaunchNotifEmbed(nextLaunchJSON)
                        for channelID in subbedChannelIDs:
                            channel = client.get_channel(channelID)
                            await safeSend(client, channel, embed=notifEmbed)

        # Save any changed data to redis
        await redisConn.set("launchNotifSent", launchNotifSent)
        await redisConn.set("latestLaunchInfoEmbedDict", latestLaunchInfoEmbedDict)

        await asyncio.sleep(ONE_MINUTE * API_CHECK_INTERVAL)

async def reaper(client):
    """
    Every $reaperInterval check for non-existant (dead) channels in subbedChannelIDs
    and remove them
    Essentially garbage collection for the channel list
    """
    await client.wait_until_ready()
    logger.info("Started")
    while not client.is_closed:
        subbedChannelIDs = await redisConn.get("subscribedChannels", obj=True)
        for channelID in subbedChannelIDs:
            # Returns None if the channel ID does not exist OR the bot cannot "see" the channel
            if client.get_channel(channelID) == None:
                # No duplicate elements in the list so remove(value) will always work
                subbedChannelIDs.remove(channelID)
                logger.info(f"{channelID} is not a valid ID, removing from db")
        await redisConn.set("subscribedChannels", subbedChannelIDs)
        await asyncio.sleep(ONE_MINUTE * REAPER_INTERVAL)
