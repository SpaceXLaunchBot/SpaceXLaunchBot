"""
Gather and show basic stats about the bot:
 - How many servers it is in
 - How many clients it is serving
 - How many subscribed channels there are
"""

import sys
sys.path.append("..")

from general import warning
import discord
import utils
import os

warning()  # Ask/show user important stuff

launchNotifDict = utils.loadDict()

try:
    token = os.environ["SpaceXLaunchBotToken"]
except KeyError:
    utils.err("Environment Variable \"SpaceXLaunchBotToken\" cannot be found")

client = discord.Client()

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="with Elon"))

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

    await client.logout()

client.run(token)
