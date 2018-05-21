from datetime import datetime, timedelta
import asyncio
import logging

from modules import embedGenerators, spacexAPI, utils, fs

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
    while not client.is_closed:
        nextLaunchJSON = await spacexAPI.getNextLaunchJSON()
        if nextLaunchJSON == 0:
            logger.warning("nextLaunchJSON returned 0, skipping this cycle")
            pass  # Error, wait for next loop/cycle
        
        else:
            launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            
            with await fs.localDataLock:
                if fs.localData["latestLaunchInfoEmbed"].to_dict() == launchInfoEmbed.to_dict():
                    pass
                else:
                    logger.info("Launch info changed, sending notifications")

                    fs.localData["launchNotifSent"] = False
                    fs.localData["latestLaunchInfoEmbed"] = launchInfoEmbed

                    # new launch found, send all "subscribed" channel the embed
                    for channelID in fs.localData["subscribedChannels"]:
                        channel = client.get_channel(channelID)
                        await safeSendLaunchInfo(client, channel, [launchInfoEmbed, launchInfoEmbedLite])

            launchTime = nextLaunchJSON["launch_date_unix"]
            if await utils.isInt(launchTime):
                
                launchTime = int(launchTime)

                # Get timestamp for the time $LAUNCH_NOTIF_DELTA minutes from now
                nextHour = (datetime.utcnow() + LAUNCH_NOTIF_DELTA).timestamp()

                # If the launch time is within the next hour
                if nextHour > launchTime:
                    logger.info("Launch happening in {}, sending notification".format(str(nextHour - launchTime)))

                    with await fs.localDataLock:
                        if fs.localData["launchNotifSent"] == False:
                            fs.localData["launchNotifSent"] = True

                            notifEmbed = await embedGenerators.getLaunchNotifEmbed(nextLaunchJSON)
                            for channelID in fs.localData["subscribedChannels"]:
                                channel = client.get_channel(channelID)
                                await safeSend(client, channel, embed=notifEmbed)

        with await fs.localDataLock:
            await fs.saveLocalData()

        await asyncio.sleep(ONE_MINUTE * API_CHECK_INTERVAL)

async def reaper(client):
    """
    Every $reaperInterval check for non-existant (dead) channels in localData["subscribedChannels"]
    and remove them
    Essentially garbage collection for the channel list
    """
    await client.wait_until_ready()
    while not client.is_closed:
        with await fs.localDataLock:
            for channelID in fs.localData["subscribedChannels"]:
                if client.get_channel(channelID) == None:
                    # No duplicate elements in the list so remove(value) will always work
                    fs.localData["subscribedChannels"].remove(channelID)
                    logger.info("{} is not a valid ID, removing from localData".format(channelID))
        await asyncio.sleep(ONE_MINUTE * REAPER_INTERVAL)
