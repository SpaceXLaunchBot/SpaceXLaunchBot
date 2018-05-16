"""
Gather and show basic stats about the bot:
 - How many servers it is in
 - How many clients it is serving
 - How many subscribed channels there are
"""

import sys
sys.path.append("..")

from errors import fatalError
from general import warning
import discord
import fs
import os

warning()  # Ask/show user important stuff

localData = fs.loadLocalData()

try:
    token = os.environ["SpaceXLaunchBotToken"]
except KeyError:
    fatalError("Environment Variable \"SpaceXLaunchBotToken\" cannot be found")

client = discord.Client()

@client.event
async def on_ready():

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

    await client.logout()

client.run(token)
