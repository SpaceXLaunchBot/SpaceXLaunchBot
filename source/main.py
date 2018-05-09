from datetime import datetime, timedelta
from threading import Lock
import discord
import asyncio
import os

import utils
from discordUtils import safeSendText, safeSendEmbed
from api import getNextLaunchJSON, getLaunchInfoEmbed, getLaunchNotifEmbed, APIErrorEmbed, generalErrorEmbed

PREFIX = "!"

"""
localData is a dictionary that has a lock (as it is accessed a lot in multiple functions) and is used
to store multiple things:
 - A list of channel IDs that are subscribed
 - The latest launch information embed that was sent
 - Whether or not an active launch notification has been sent for the current launch
Tjos is saved to and loaded from a file (so it persists through reboots/updates)
"""
# TODO: In variable & function names, distinguish more between launch information embeds, and active launch notification embeds
localData = utils.loadDict()
localDataLock = Lock()  # locks access when saving / loading

client = discord.Client()

try:
    token = os.environ["SpaceXLaunchBotToken"]
except KeyError:
    utils.err("Environment Variable \"SpaceXLaunchBotToken\" cannot be found")

async def notificationBackgroundTask():
    """
    Every 1/2 hour:
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
                    await utils.saveDict(localData)

                    # new launch found, send all "subscribed" channel the embed
                    for channelID in localData["subscribedChannels"]:
                        channel = client.get_channel(channelID)
                        await safeSendEmbed(client, channel, [launchInfoEmbed, launchInfoEmbedLite])

            launchTime = nextLaunchJSON["launch_date_unix"]
            launchTimeIsInt = await utils.isInt(launchTime)
            if launchTimeIsInt:

                # Unix timestamp of next hour
                nextHour = (datetime.now() + timedelta(hours=1)).timestamp()
                # If the launch time is within the next hour
                if nextHour > int(launchTime):

                    if localData["launchNotifSent"] == False:
                        localData["launchNotifSent"] = True
                        with localDataLock:
                            await utils.saveDict(localData)

                        notifEmbed = await getLaunchNotifEmbed(nextLaunchJSON)
                        for channelID in localData["subscribedChannels"]:
                            channel = client.get_channel(channelID)
                            await safeSendEmbed(client, channel, [notifEmbed])

        await asyncio.sleep(60 * 30) # task runs every 30 minutes

@client.event
async def on_message(message):
    try:
        userIsAdmin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        # Happens if user has no roles
        userIsAdmin = False
    
    if message.content.startswith(PREFIX + "nextlaunch"):
        nextLaunchJSON = await getNextLaunchJSON()
        if nextLaunchJSON == 0:
            launchInfoEmbed, launchInfoEmbedLite = APIErrorEmbed, APIErrorEmbed
        else:
            launchInfoEmbed, launchInfoEmbedLite = await getLaunchInfoEmbed(nextLaunchJSON)
        await safeSendEmbed(client, message.channel, [launchInfoEmbed, launchInfoEmbedLite])

    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        replyMsg = "This channel has been added to the launch notification service"
        with localDataLock:
            if message.channel.id not in localData["subscribedChannels"]:
                localData["subscribedChannels"].append(message.channel.id)
                await utils.saveDict(localData)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"
        await safeSendText(client, message.channel, replyMsg)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        replyMsg = "This channel has been removed from the launch notification service"
        with localDataLock:
            try:
                localData["subscribedChannels"].remove(message.channel.id)
                await utils.saveDict(localData)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
        await safeSendText(client, message.channel, replyMsg)

    elif message.content.startswith(PREFIX + "info"):
        await safeSendText(client, message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await safeSendText(client, message.channel, utils.helpText.format(prefix=PREFIX))

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="with Elon"))

    with localDataLock:
        totalSubbed = len(localData["subscribedChannels"])
    totalServers = len(list(client.servers))
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

client.loop.create_task(notificationBackgroundTask())
client.run(token)
