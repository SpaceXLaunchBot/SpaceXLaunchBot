import discord
import asyncio
import os

import utils
import launchAPI

PREFIX = "!"

client = discord.Client()
try:
    token = os.environ["SpaceX-Launch-Bot-Token"]
except KeyError:
    utils.err("Environment Variable \"SpaceX-Launch-Bot-Token\" cannot be found")
    
@client.event
async def on_ready():
    print("\nLogged into Discord API")
    print("\tUsername: {}\n\tClientID:{}".format(client.user.name, client.user.id))

@client.event
async def on_message(message):
    if message.content.startswith(PREFIX + "addchannel"):
        pass
    elif message.content.startswith(PREFIX + "nextlaunchshort"):
        embed = await launchAPI.getNextLaunchEmbed()
        await client.send_message(message.channel, embed=embed)
    elif message.content.startswith(PREFIX + "nextlaunch"):
        pass

client.run(token)
