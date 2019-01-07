"""
Async tasks to run in the background
"""

import asyncio
import logging
from aredis import RedisError
from datetime import datetime, timedelta

from modules.redisClient import redisConn
from modules import embedGenerators, structure, apis

logger = logging.getLogger(__name__)

ONE_MINUTE = 60  # Just makes things a little more readable
API_CHECK_INTERVAL = structure.config["apiCheckInterval"]
LAUNCH_NOTIF_DELTA = timedelta(minutes=structure.config["launchNotificationDelta"])


async def notificationTask(client):
    """
    TODO: Tidy this up
    Every API_CHECK_INTERVAL minutes:
    If the embed has changed, something new has happened so send
        all channels an embed with updated info
    If the time of the next upcoming launch is within the next hour,
        send out a notification embed alerting people
    """
    await client.wait_until_ready()
    logger.info("Started")
    while not client.is_closed():
        try:
            if not await redisConn.exists("subscribedChannels"):
                # No subscribedChannels SET, no channels to send notifications to
                pass

            else:
                channelsToRemove = []

                nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON()

                subbedChannelIDs = await redisConn.smembers("subscribedChannels")
                notificationTaskStore = await redisConn.getNotificationTaskStore()

                # Redis returns a set of strings, we want integers (a tuple is used
                # for memory-saving reasons)
                subbedChannelIDs = (int(cid) for cid in subbedChannelIDs)

                launchingSoonNotifSent = notificationTaskStore["launchingSoonNotifSent"]
                latestLaunchInfoEmbedDict = notificationTaskStore[
                    "latestLaunchInfoEmbedDict"
                ]

                launchInfoEmbed, launchInfoEmbedSmall = await embedGenerators.genLaunchInfoEmbeds(
                    nextLaunchJSON
                )
                launchInfoEmbedDict = (
                    launchInfoEmbed.to_dict()
                )  # Only calculate this once

                # Launch information message
                if latestLaunchInfoEmbedDict != launchInfoEmbedDict:
                    logger.info("Launch info changed, sending notifications")

                    launchingSoonNotifSent = "False"
                    latestLaunchInfoEmbedDict = launchInfoEmbedDict

                    # New launch found, send all "subscribed" channels the embed
                    for channelID in subbedChannelIDs:
                        channel = client.get_channel(channelID)
                        if channel == None:
                            channelsToRemove.append(channelID)
                        else:
                            await client.safeSendLaunchInfo(
                                channel,
                                launchInfoEmbed,
                                launchInfoEmbedSmall,
                                sendErr=False,
                            )

                # TODO: Move into new task that runs more frequently so the message can say in how many mins the launch will be happening
                # Launching soon message
                launchTimestamp = await structure.convertToInt(
                    nextLaunchJSON["launch_date_unix"]
                )
                # If launchTimestamp is an int carry on, else it is TBA
                if launchTimestamp:

                    # Get timestamp for the time LAUNCH_NOTIF_DELTA from now
                    currentTime = datetime.utcnow()
                    timePlusDelta = (currentTime + LAUNCH_NOTIF_DELTA).timestamp()

                    # If the launch time is within the next LAUNCH_NOTIF_DELTA
                    # and if the launchTimestamp is not in the past
                    if (
                        timePlusDelta >= launchTimestamp
                        and launchTimestamp >= currentTime.timestamp()
                    ):
                        if launchingSoonNotifSent == "False":

                            logger.info(
                                f"Launch happening within {LAUNCH_NOTIF_DELTA}, sending notification"
                            )
                            launchingSoonNotifSent = "True"
                            launchingSoonEmbed = await embedGenerators.genLaunchingSoonEmbed(
                                nextLaunchJSON
                            )

                            for channelID in subbedChannelIDs:
                                channel = client.get_channel(channelID)
                                if channel == None:
                                    channelsToRemove.append(channelID)
                                else:
                                    await client.safeSend(channel, launchingSoonEmbed)

                                    try:
                                        guildSettings = await redisConn.getGuildSettings(
                                            channel.guild.id
                                        )
                                    except RedisError:
                                        # If a redis error occurs here, it is better to send out
                                        # the remaining notifications than to exit this block
                                        pass
                                    else:
                                        # If there are settings saved for the guild
                                        if guildSettings != 0:
                                            # Ping the roles/users (mentions) requested
                                            await client.safeSend(
                                                channel, guildSettings["rolesToMention"]
                                            )

                        else:
                            logger.info(
                                f"Launch happening within {LAUNCH_NOTIF_DELTA}, launchingSoonNotifSent is {launchingSoonNotifSent}"
                            )

                # Save any changed data to redis
                # Remove channels that we can't access anymore
                for channelID in channelsToRemove:
                    logger.info(f"{channelID} is not a valid channel ID, removing")
                    await redisConn.srem(
                        "subscribedChannels", str(channelID).encode("UTF-8")
                    )

                await redisConn.setNotificationTaskStore(
                    launchingSoonNotifSent, latestLaunchInfoEmbedDict
                )

        except RedisError as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
        except Exception as e:
            logger.error(f"Task failed:  {type(e).__name__}: {e}")
        finally:
            await asyncio.sleep(ONE_MINUTE * API_CHECK_INTERVAL)
