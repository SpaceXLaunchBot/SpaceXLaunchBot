"""
Async tasks to run in the background
"""

from datetime import datetime, timedelta
from copy import deepcopy
import asyncio
import logging
import pickle

from modules.redisClient import redisConn

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
    while not client.is_closed():
        
        """
        Getting everything and then checking for errors probably isn't very
        efficient but since this is run on a set time loop and runs in the
        background, it shouldn't matter much...
        """

        subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
        latestLaunchInfoEmbedDict = await redisConn.getLatestLaunchInfoEmbedDict()
        launchNotifSent = await redisConn.getLaunchNotifSent()
        nextLaunchJSON = await spacexAPI.getNextLaunchJSON()
        
        if subbedChannelsDict["err"]:
            logger.error("getSubscribedChannelIDs returned err, skipping this cycle")
            pass
        
        elif latestLaunchInfoEmbedDict == 0:
            logger.error("latestLaunchInfoEmbedDict is 0, skipping this cycle")
            pass

        elif nextLaunchJSON == 0:
            logger.error("nextLaunchJSON returned 0, skipping this cycle")
            pass  # Error, wait for next loop/cycle
        
        else:
            subbedChannelIDs = subbedChannelsDict["list"]

            launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            launchInfoEmbedDict = launchInfoEmbed.to_dict()  # Only calculate this once

            if latestLaunchInfoEmbedDict == launchInfoEmbedDict:
                pass
            else:
                logger.info("Launch info changed, sending notifications")

                launchNotifSent = "False"
                latestLaunchInfoEmbedDict = launchInfoEmbedDict

                # New launch found, send all "subscribed" channel the embed
                for channelID in subbedChannelIDs:
                    channel = client.get_channel(channelID)
                    await safeSendLaunchInfo(channel, [launchInfoEmbed, launchInfoEmbedLite])

            launchTime = nextLaunchJSON["launch_date_unix"]
            if await utils.isInt(launchTime):
                
                launchTime = int(launchTime)

                # Get timestamp for the time $LAUNCH_NOTIF_DELTA from now
                soon = (datetime.utcnow() + LAUNCH_NOTIF_DELTA).timestamp()

                # If the launch time is within the next hour
                if soon > launchTime:
                    if launchNotifSent == "False":

                        logger.info(f"Launch happening within {LAUNCH_NOTIF_DELTA}, sending notification")
                        launchNotifSent = "True"

                        notifEmbed = await embedGenerators.getLaunchNotifEmbed(nextLaunchJSON)
                        for channelID in subbedChannelIDs:
                            channel = client.get_channel(channelID)

                            guildID = channel.guild.id
                            tags = await redisConn.safeGet(guildID)
                            
                            await safeSend(channel, embed=notifEmbed)
                            if tags:
                                # Tag the roles/users requested
                                tags = pickle.loads(tags)
                                await safeSend(channel, text=tags)
                            
                    else:
                        logger.info(f"Launch happening within {LAUNCH_NOTIF_DELTA}, launchNotifSent is {launchNotifSent}")
                        
        # Save any changed data to redis
        # TODO: Grab the return value from safeSet and log an error if it didn't set properly
        await redisConn.safeSet("launchNotifSent", launchNotifSent)
        await redisConn.safeSet("latestLaunchInfoEmbedDict", latestLaunchInfoEmbedDict, True)

        await asyncio.sleep(ONE_MINUTE * API_CHECK_INTERVAL)

async def reaper(client):
    """
    Every $reaperInterval check for non-existant (dead) channels in subbedChannelIDs
    and remove them
    Essentially garbage collection for the channel list
    TODO: If parts of the Discord API goes down, this can sometimes trigger the
    removal of channels that do exist but Discord can't find them
    """
    await client.wait_until_ready()
    logger.info("Started")
    while not client.is_closed():
        subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
        subbedChannelIDs = subbedChannelsDict["list"]
        for channelID in subbedChannelIDs:
            # Returns None if the channel ID does not exist OR the bot cannot "see" the channel
            if client.get_channel(channelID) == None:
                # No duplicate elements in the list so remove(value) will always work
                subbedChannelIDs.remove(channelID)
                logger.info(f"{channelID} is not a valid ID, removing from db")
        # TODO: Grab the return value from safeSet and log an error if it didn't set properly
        await redisConn.safeSet("subscribedChannels", subbedChannelIDs, True)
        await asyncio.sleep(ONE_MINUTE * REAPER_INTERVAL)
