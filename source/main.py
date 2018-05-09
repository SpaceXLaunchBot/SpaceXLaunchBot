from threading import Lock
import discord
import asyncio
import os

import utils
from utils import safeTextMessage  # So `utils.` doesen't need to be prepended
from launchAPI import getnextLaunchJSON, getNextLaunchEmbed, APIErrorEmbed, generalErrorEmbed

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
            nextLaunchEmbed, nextLaunchEmbedLite = await getNextLaunchEmbed(nextLaunchJSON)
            
            with localDataLock:
                if localData["nextLaunchEmbed"].to_dict() == nextLaunchEmbed.to_dict():
                    pass
                else:
                    # Add and save new launch info
                    localData["nextLaunchEmbed"] = nextLaunchEmbed
                    utils.saveDict(localData)
                
                    # new launch found, send all "subscribed" channel the embed
                    for channelID in localData["subscribedChannels"]:
                        channel = client.get_channel(channelID)
                        await sendLaunchEmbed(channel, nextLaunchEmbed, nextLaunchEmbedLite)

        """
        TODO:
         - Have a variable called launchNotifSent in localData
        
        # Place in above code
        if launch has changed
            localData["launchNotifSent"] = False

        # Send a notification if the launch is within the next hour
        # Don't send another notification if one has already been sent for the current launch time
        # If the launch has changed, send another notification/embed with updated info

        launchTime = nextLaunchJSON["launch_date_unix"]
        if isInt(launchTime):
            if unix_Within_Next_Hour(launchTime):
                if localData["launchNotifSent"] == False:
                    localData["launchNotifSent"] = True
                    saveDict(localData)
                    e = await getLaunchNotifEmbed(nextLaunchJSON)
                    await sendLaunchNotifiEmbed(e)
        """

        await asyncio.sleep(60 * 30) # task runs every 30 minutes

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
            nextLaunchEmbed, nextLaunchEmbedLite = await getNextLaunchEmbed(nextLaunchJSON)
        await sendLaunchEmbed(message.channel, nextLaunchEmbed, nextLaunchEmbedLite)

    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        replyMsg = "This channel has been added to the launch notification service"
        with localDataLock:
            if message.channel.id not in localData["subscribedChannels"]:
                localData["subscribedChannels"].append(message.channel.id)
                utils.saveDict(localData)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"
        await safeTextMessage(client, message.channel, replyMsg)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        replyMsg = "This channel has been removed from the launch notification service"
        with localDataLock:
            try:
                localData["subscribedChannels"].remove(message.channel.id)
                utils.saveDict(localData)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
        await safeTextMessage(client, message.channel, replyMsg)

    elif message.content.startswith(PREFIX + "info"):
        await safeTextMessage(client, message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await safeTextMessage(client, message.channel, utils.helpText.format(prefix=PREFIX))

client.loop.create_task(nextLaunchBackgroundTask())
client.run(token)
