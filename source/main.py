from datetime import datetime, timedelta
from os import environ as envVars
from threading import Lock
import discord
import asyncio

import utils
from dblAPI import dblClient
from api import getNextLaunchJSON, apiErrorEmbed
from embedGenerators import getLaunchInfoEmbed, getLaunchNotifEmbed
from discordUtils import safeSendText, safeSendEmbed, safeSendLaunchInfoEmbeds

# TODO: Replace print statements with propper logging

config = utils.loadConfig()

"""
Constants / important variables
"""
# The prefix needed to activate a command
PREFIX = config["commandPrefix"]
# The interval time, in minutes, between checking the API for updates - must be an int
API_CHECK_INTERVAL = config["apiCheckInterval"]
# How far into the future to look for launches that are happening soon. Should be at least $API_CHECK_INTERVAL * 2
LAUNCH_NOTIF_DELTA = timedelta(minutes = config["launchNotificationDelta"])

"""
localData is a dictionary that has a lock (as it is accessed a lot in multiple functions) and is used
to store multiple things:
 - A list of channel IDs that are subscribed
 - The latest launch information embed that was sent
 - Whether or not an active launch notification has been sent for the current launch
This is saved to and loaded from a file (so it persists through reboots/updates)
"""
localData = utils.loadLocalData()
localDataLock = Lock()  # locks access when saving / loading

client = discord.Client()
try:
    token = envVars["SpaceXLaunchBotToken"]
except KeyError:
    utils.err("Environment Variable \"SpaceXLaunchBotToken\" cannot be found")

async def notificationBackgroundTask():
    """
    Every $API_CHECK_INTERVAL minutes:
    If the embed has changed, something new has happened so send
        all channels an embed with updated info
    If the time of the next upcoming launch is within the next hour,
        send out a notification embed alerting people
    """
    await client.wait_until_ready()
    while not client.is_closed:
        nextLaunchJSON = await getNextLaunchJSON()
        if nextLaunchJSON == 0:
            pass  # Error, do nothing, wait for 30 more mins
        
        else:
            launchInfoEmbed, launchInfoEmbedLite = await getLaunchInfoEmbed(nextLaunchJSON)
            
            with localDataLock:
                if localData["latestLaunchInfoEmbed"].to_dict() == launchInfoEmbed.to_dict():
                    pass
                else:
                    # Launch info has changed, set variables
                    localData["launchNotifSent"] = False
                    localData["latestLaunchInfoEmbed"] = launchInfoEmbed

                    # new launch found, send all "subscribed" channel the embed
                    for channelID in localData["subscribedChannels"]:
                        channel = client.get_channel(channelID)
                        await safeSendLaunchInfoEmbeds(client, channel, [launchInfoEmbed, launchInfoEmbedLite])

            launchTime = nextLaunchJSON["launch_date_unix"]
            if await utils.isInt(launchTime):

                # Get timestamp for the time $LAUNCH_NOTIF_DELTA minutes from now
                nextHour = (datetime.utcnow() + LAUNCH_NOTIF_DELTA).timestamp()

                # If the launch time is within the next hour
                if nextHour > int(launchTime):

                        with localDataLock:
                            if localData["launchNotifSent"] == False:
                                localData["launchNotifSent"] = True

                                notifEmbed = await getLaunchNotifEmbed(nextLaunchJSON)
                                for channelID in localData["subscribedChannels"]:
                                    channel = client.get_channel(channelID)
                                    await safeSendEmbed(client, channel, notifEmbed)

        with localDataLock:
            await utils.saveLocalData(localData)

        await asyncio.sleep(60 * API_CHECK_INTERVAL)

@client.event
async def on_message(message):
    if message.author.bot:
        # Don't reply to bots (includes self)
        return

    try:
        userIsAdmin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        # Happens if user has no roles
        userIsAdmin = False
    
    if message.content.startswith(PREFIX + "nextlaunch"):
        # TODO: Maybe just pull latest embed from localData instead of requesting every time?
        nextLaunchJSON = await getNextLaunchJSON()
        if nextLaunchJSON == 0:
            launchInfoEmbed, launchInfoEmbedLite = apiErrorEmbed, apiErrorEmbed
        else:
            launchInfoEmbed, launchInfoEmbedLite = await getLaunchInfoEmbed(nextLaunchJSON)
        await safeSendLaunchInfoEmbeds(client, message.channel, [launchInfoEmbed, launchInfoEmbedLite])

    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        replyMsg = "This channel has been added to the launch notification service"
        with localDataLock:
            if message.channel.id not in localData["subscribedChannels"]:
                localData["subscribedChannels"].append(message.channel.id)
                await utils.saveLocalData(localData)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"
        await safeSendText(client, message.channel, replyMsg)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        replyMsg = "This channel has been removed from the launch notification service"
        with localDataLock:
            try:
                localData["subscribedChannels"].remove(message.channel.id)
                await utils.saveLocalData(localData)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
        await safeSendText(client, message.channel, replyMsg)

    elif message.content.startswith(PREFIX + "info"):
        await safeSendText(client, message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await safeSendText(client, message.channel, utils.helpText.format(prefix=PREFIX))

@client.event
async def on_ready():
    global dbl  # Can't define this until client is ready
    dbl = dblClient(client)

    await client.change_presence(game=discord.Game(name="with Elon"))

    with localDataLock:
        totalSubbed = len(localData["subscribedChannels"])
    totalServers = len(client.servers)
    totalClients = 0
    for server in client.servers:
        totalClients += len(server.members)

    print("\nLogged into Discord API\n")
    print("Username: {}\nClientID: {}\n\nConnected to {} servers\nConnected to {} subscribed channels\nServing {} clients".format(
        client.user.name,
        client.user.id,
        totalServers,
        totalSubbed,
        totalClients
    ))
    await dbl.updateServerCount(totalServers)

@client.event
async def on_server_join(server):
    await dbl.updateServerCount(len(client.servers))

@client.event
async def on_server_remove(server):
    await dbl.updateServerCount(len(client.servers))

client.loop.create_task(notificationBackgroundTask())
client.run(token)
