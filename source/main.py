from threading import Lock
import discord
import asyncio
import pickle
import os

import utils
from launchAPI import getnextLaunchJSON, getnextLaunchEmbed, APIErrorEmbed, getLiteEmbed

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

async def nextLaunchBackgroundTask():
    """
    Every 1/2 hour, get latest JSON & format an embed. If the embed has changed since the last 1/2 hour, then
    something new has happened to send all channels an update. Else do nothing
    """
    await client.wait_until_ready()
    while not client.is_closed:
        newLaunch = True

        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            pass  # Error, do nothing, wait for 30 more mins
        
        else:
            nextLaunchEmbed = await getnextLaunchEmbed(nextLaunchJSON)
            liteEmbed = await getLiteEmbed(nextLaunchJSON)  # Generate now just in case
            nextLaunchEmbedPickled = pickle.dumps(nextLaunchEmbed, utils.pickleProtocol)
            
            with launchNotifDictLock:
                if launchNotifDict["nextLaunchEmbedPickled"] == nextLaunchEmbedPickled:
                    newLaunch = False
                else:
                    # Add and save new launch info
                    launchNotifDict["nextLaunchEmbedPickled"] = nextLaunchEmbedPickled
                    utils.saveDict(launchNotifDict)
                
            if newLaunch:
                # new launch found, send all "subscribed" channel the embed
                for channelID in launchNotifDict["subscribedChannels"]:
                    channel = discord.Object(id=channelID)
                    try:
                        await client.send_message(channel, embed=nextLaunchEmbed)
                    except discord.errors.HTTPException:
                        # getnextLaunchEmbed was too big, send lite version
                        await client.send_message(channel, embed=liteEmbed)

        await asyncio.sleep(60 * 30) # task runs every 30 minutes

@client.event
async def on_ready():
    with launchNotifDictLock:
        subbedLen = len(launchNotifDict["subscribedChannels"])
    await client.change_presence(game=discord.Game(name="with Elon"))
    servers = list(client.servers)
    
    totalClients = 0
    for server in client.servers:
        totalClients += len(server.members)

    print("\nLogged into Discord API\n")
    print("Username: {}\nClientID: {}\n\nConnected to {} servers:\n{}\n\nConnected to {} subscribed channels\n\nServing {} clients".format(
        client.user.name,
        client.user.id,
        len(servers),
        "\n".join([n.name for n in servers]),
        subbedLen,
        totalClients
    ))

@client.event
async def on_message(message):
    try:
        userIsAdmin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        userIsAdmin = False
    
    if message.content.startswith(PREFIX + "nextlaunch"):
        # Send latest launch JSON embed to message.channel
        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            embed = APIErrorEmbed
        else:
            embed = await getnextLaunchEmbed(nextLaunchJSON)
        try:
            await client.send_message(message.channel, embed=embed)
        except discord.errors.HTTPException:
            # getnextLaunchEmbed was too big, send lite version
            embed = await getLiteEmbed(nextLaunchJSON)
            await client.send_message(message.channel, embed=embed)

    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        replyMsg = "This channel has been added to the launch notification service"
        with launchNotifDictLock:
            if message.channel.id not in launchNotifDict["subscribedChannels"]:
                launchNotifDict["subscribedChannels"].append(message.channel.id)
                utils.saveDict(launchNotifDict)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"
        await client.send_message(message.channel, replyMsg)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        replyMsg = "This channel has been removed from the launch notification service"
        with launchNotifDictLock:
            try:
                launchNotifDict["subscribedChannels"].remove(message.channel.id)
                utils.saveDict(launchNotifDict)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
        await client.send_message(message.channel, replyMsg)

    elif message.content.startswith(PREFIX + "info"):
        await client.send_message(message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await client.send_message(message.channel, utils.helpText.format(prefix=PREFIX))

client.loop.create_task(nextLaunchBackgroundTask())
client.run(token)
