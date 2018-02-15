from threading import Lock
import discord
import asyncio
import os

import utils
from launchAPI import getnextLaunchJSON, getnextLaunchEmbed, APIErrorEmbed

PREFIX = "!"
launchNotifDict = utils.loadDict()
dictLock = Lock()  # locks access when saving / loading
client = discord.Client()
try:
    token = os.environ["SpaceXLaunchBotToken"]
except KeyError:
    utils.err("Environment Variable \"SpaceXLaunchBotToken\" cannot be found")

async def nextLaunchBackgroundTask():
    """
    Every 1/2 hour, update dict with latest launch then see if subs need updating
    """
    await client.wait_until_ready()
    while not client.is_closed:
        newLaunch = True

        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            pass  # Error, do nothing, wait for 30 more mins
        else:
            with dictLock:
                if launchNotifDict["nextLaunchJSON"] == nextLaunchJSON:
                    newLaunch = False
                else:
                    # Add and save new launch info
                    launchNotifDict["nextLaunchJSON"] = nextLaunchJSON
                    utils.saveDict(launchNotifDict)
                
            if newLaunch:
                # new launch found, send all "subscribed" channel the embed
                embed = await getnextLaunchEmbed(nextLaunchJSON)
                for channelID in launchNotifDict["subscribedChannels"]:
                    await client.send_message(discord.Object(id=channelID), embed=embed)

        await asyncio.sleep(60 * 30) # task runs every 30 minutes

@client.event
async def on_ready():
    with dictLock:
        subbedLen = len(launchNotifDict["subscribedChannels"])
    await client.change_presence(game=discord.Game(name="with Elon"))
    servers = list(client.servers)
    print("\nLogged into Discord API\n")
    print("Username: {}\nClientID: {}\n\nConnected to {} server(s):\n{}\n\nConnected to {} subscribed channels".format(
        client.user.name,
        client.user.id,
        len(servers),
        "\n".join([n.name for n in servers],
        subbedLen)
    ))

@client.event
async def on_message(message):

    if message.content.startswith(PREFIX + "nextlaunch"):
        # Send latest launch JSON embed to message.channel
        nextLaunchJSON = await getnextLaunchJSON()
        if nextLaunchJSON == 0:
            embed = APIErrorEmbed
        else:
            embed = await getnextLaunchEmbed(nextLaunchJSON)
        await client.send_message(message.channel, embed=embed)
    
    elif message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        with dictLock:
            launchNotifDict["subscribedChannels"].append(message.channel.id)
            utils.saveDict(launchNotifDict)
        await client.send_message(message.channel, "This channel has been added to the launch notification service")
    
    elif message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        with dictLock:
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
