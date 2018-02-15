from threading import Lock
import discord
import asyncio
import pickle
import os

import utils
from launchAPI import getnextLaunchJSON, getnextLaunchEmbed, APIErrorEmbed

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
                    await client.send_message(discord.Object(id=channelID), embed=nextLaunchEmbed)

        await asyncio.sleep(60 * 30) # task runs every 30 minutes

@client.event
async def on_ready():
    with launchNotifDictLock:
        subbedLen = len(launchNotifDict["subscribedChannels"])
    await client.change_presence(game=discord.Game(name="with Elon"))
    servers = list(client.servers)
    print("\nLogged into Discord API\n")
    print("Username: {}\nClientID: {}\n\nConnected to {} server(s):\n{}\n\nConnected to {} subscribed channels".format(
        client.user.name,
        client.user.id,
        len(servers),
        "\n".join([n.name for n in servers]),
        subbedLen
    ))

@client.event
async def on_message(message):
    userIsAdmin = message.author.permissions_in(message.channel).administrator
    
    if message.content.startswith(PREFIX + "nextlaunch"):
        # Send latest launch JSON embed to message.channel
        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            embed = APIErrorEmbed
        else:
            embed = await getnextLaunchEmbed(nextLaunchJSON)
        await client.send_message(message.channel, embed=embed)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        with launchNotifDictLock:
            launchNotifDict["subscribedChannels"].append(message.channel.id)
            utils.saveDict(launchNotifDict)
        await client.send_message(message.channel, "This channel has been added to the launch notification service")
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        with launchNotifDictLock:
            try:
                launchNotifDict["subscribedChannels"].remove(message.channel.id)
                utils.saveDict(launchNotifDict)
            except ValueError:
                pass  # Channel was not in subscribedChannels
        await client.send_message(message.channel, "This channel has been removed from the launch notification service")

    elif message.content.startswith(PREFIX + "info"):
        await client.send_message(message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await client.send_message(message.channel, utils.helpText.format(prefix=PREFIX))

client.loop.create_task(nextLaunchBackgroundTask())
client.run(token)
