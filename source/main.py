from threading import Lock
import discord
import asyncio
import os

import utils
from utils import safeTextMessage  # So `utils.` doesen't need to be prepended
from launchAPI import getnextLaunchJSON, getnextLaunchEmbed, APIErrorEmbed, getnextLaunchLiteEmbed, generalErrorEmbed

PREFIX = "!"

"""
launchNotifDict is a dictionary that has a lock (as it is accessed a lot in multiple functions) and is used
to store 2 things: the list of channel IDs that are subscribed, and the latest embed that was sent. It is
what is saved to and loaded from a file (so it persists through reboots/updates)
"""
launchNotifDict = utils.loadDict()
launchNotifDictLock = Lock()  # locks access when saving / loading

client = discord.Client()

try:
    token = os.environ["SpaceXLaunchBotToken"]
except KeyError:
    utils.err("Environment Variable \"SpaceXLaunchBotToken\" cannot be found")

async def sendLaunchEmbed(channel, nextLaunchEmbed, nextLaunchEmbedLite):
    """
    General func for sending a channel the latest launch embed
    """
    for embed in [nextLaunchEmbed, nextLaunchEmbedLite]:
        try:
            return await client.send_message(channel, embed=embed)
        except discord.errors.HTTPException:
            pass
        except (discord.errors.Forbidden, discord.errors.InvalidArgument):
            # TODO: double check if InvalidArgument when a channel does not exist
            return  # No permission to message this channel, or this channel does not exist, stop trying
    await client.send_message(channel, embed=generalErrorEmbed)

async def nextLaunchBackgroundTask():
    """
    Every 1/2 hour, get latest JSON & format an embed. If the embed has changed since the last 1/2 hour, then
    something new has happened to send all channels an update. Else do nothing
    """
    await client.wait_until_ready()
    while not client.is_closed:
        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            pass  # Error, do nothing, wait for 30 more mins
        
        else:
            nextLaunchEmbed = await getnextLaunchEmbed(nextLaunchJSON)
            
            with launchNotifDictLock:
                if launchNotifDict["nextLaunchEmbed"].to_dict() == nextLaunchEmbed.to_dict():
                    pass
                else:
                    # Add and save new launch info
                    launchNotifDict["nextLaunchEmbed"] = nextLaunchEmbed
                    utils.saveDict(launchNotifDict)
                
                    nextLaunchEmbedLite = await getnextLaunchLiteEmbed(nextLaunchJSON)
                    # new launch found, send all "subscribed" channel the embed
                    for channelID in launchNotifDict["subscribedChannels"]:
                        channel = client.get_channel(channelID)
                        await sendLaunchEmbed(channel, nextLaunchEmbed, nextLaunchEmbedLite)

        await asyncio.sleep(60 * 30) # task runs every 30 minutes

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="with Elon"))

    with launchNotifDictLock:
        totalSubbed = len(launchNotifDict["subscribedChannels"])
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

@client.event
async def on_message(message):
    try:
        userIsAdmin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        # Happens if user has no roles
        userIsAdmin = False
    
    if message.content.startswith(PREFIX + "nextlaunch"):
        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            nextLaunchEmbed = APIErrorEmbed
            nextLaunchEmbedLite = APIErrorEmbed
        else:
            nextLaunchEmbed = await getnextLaunchEmbed(nextLaunchJSON)
            nextLaunchEmbedLite = await getnextLaunchLiteEmbed(nextLaunchJSON)
        await sendLaunchEmbed(message.channel, nextLaunchEmbed, nextLaunchEmbedLite)

    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        replyMsg = "This channel has been added to the launch notification service"
        with launchNotifDictLock:
            if message.channel.id not in launchNotifDict["subscribedChannels"]:
                launchNotifDict["subscribedChannels"].append(message.channel.id)
                utils.saveDict(launchNotifDict)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"
        await safeTextMessage(client, message.channel, replyMsg)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        replyMsg = "This channel has been removed from the launch notification service"
        with launchNotifDictLock:
            try:
                launchNotifDict["subscribedChannels"].remove(message.channel.id)
                utils.saveDict(launchNotifDict)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
        await safeTextMessage(client, message.channel, replyMsg)

    elif message.content.startswith(PREFIX + "info"):
        await safeTextMessage(client, message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await safeTextMessage(client, message.channel, utils.helpText.format(prefix=PREFIX))

client.loop.create_task(nextLaunchBackgroundTask())
client.run(token)
