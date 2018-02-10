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
    servers = list(client.servers)
    print("\nLogged into Discord API\n")
    print("Username: {}\nClientID: {}\n\nConnected to {} server(s):\n{}".format(
        client.user.name,
        client.user.id,
        len(servers),
        "\n".join([n.name for n in servers])
    ))

@client.event
async def on_message(message):
    if message.content.startswith(PREFIX + "addchannel"):
        await client.send_message(message.channel, "addchannel currently not implemented")
    elif message.content.startswith(PREFIX + "nextlaunch"):
        embed = await launchAPI.getNextLaunchEmbed()
        await client.send_message(message.channel, embed=embed)
    elif message.content.startswith(PREFIX + "info"):
        await client.send_message(message.channel, utils.botInfo)
    elif message.content.startswith(PREFIX + "help"):
        await client.send_message(message.channel, utils.helpText.format(prefix=PREFIX))

client.run(token)
