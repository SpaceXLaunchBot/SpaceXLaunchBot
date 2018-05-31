"""
Run the bot and start everything
"""

# Script has started, get time (for startup time) and show user we have started
# Do this before other imports as they can take a few seconds
from time import time
startupTime = time()
print("Init started")

# Built-ins and 3rd party modules
import logging
import discord
from os import path

# Setup logging stuff
from modules import logSetup
logSetup.setup()

# Import everything else (once logging is set up)
from modules import fs, utils, errors, dblAPI, spacexAPI, staticMessages, embedGenerators, backgroundTasks
from modules.discordUtils import safeSend, safeSendLaunchInfo

logger = logging.getLogger(__name__)
logger.info("Starting bot")

# Important vars
PREFIX = fs.config["commandPrefix"]
discordToken = utils.loadEnvVar("SpaceXLaunchBotToken")
client = discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        # Don't reply to bots (includes self)
        return

    try:
        userIsAdmin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        # Happens if user has no roles
        userIsAdmin = False

    # Commands can be in any case
    message.content = message.content.lower()
    
    if message.content.startswith(PREFIX + "nextlaunch"):
        # TODO: Maybe just pull latest embed from localData instead of requesting every time?
        nextLaunchJSON = await spacexAPI.getNextLaunchJSON()
        if nextLaunchJSON == 0:
            launchInfoEmbed, launchInfoEmbedLite = errors.apiErrorEmbed, errors.apiErrorEmbed
        else:
            launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
        await safeSendLaunchInfo(client, message.channel, [launchInfoEmbed, launchInfoEmbedLite])

    elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        # Add channel ID to subbed channels
        replyMsg = "This channel has been added to the launch notification service"
        with await fs.localDataLock:
            if message.channel.id not in fs.localData["subscribedChannels"]:
                fs.localData["subscribedChannels"].append(message.channel.id)
                await fs.saveLocalData()
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"
        await safeSend(client, message.channel, text=replyMsg)
    
    elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        # Remove channel ID from subbed channels
        replyMsg = "This channel has been removed from the launch notification service"
        with await fs.localDataLock:
            try:
                # No duplicate elements in the list so remove(value) will always work
                fs.localData["subscribedChannels"].remove(message.channel.id)
                await fs.saveLocalData()
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
        await safeSend(client, message.channel, text=replyMsg)

    elif message.content.startswith(PREFIX + "info"):
        await safeSend(client, message.channel, embed=staticMessages.infoEmbed)
    elif message.content.startswith(PREFIX + "help"):
        await safeSend(client, message.channel, embed=staticMessages.helpEmbed)

@client.event
async def on_ready():
    global dbl  # Can't define this until client is ready
    dbl = dblAPI.dblClient(client)

    await client.change_presence(game=discord.Game(name="with Elon"))

    with await fs.localDataLock:
        totalSubbed = len(fs.localData["subscribedChannels"])
    totalServers = len(client.servers)
    totalClients = 0
    for server in client.servers:
        totalClients += len(server.members)   
    
    logger.info(f"Username: {client.user.name}")
    logger.info(f"ClientID: {client.user.id}")
    logger.info(f"Connected to {totalServers} servers")
    logger.info(f"Connected to {totalSubbed} subscribed channels")
    logger.info(f"Serving {totalClients} clients")

    formattedTime = str(time() - startupTime)[0:4]
    print(f"Bot ready\nStarted in: {formattedTime}s")
    logger.info(f"Started in: {formattedTime}s")

    await dbl.updateServerCount(totalServers)

@client.event
async def on_server_join(server):
    await dbl.updateServerCount(len(client.servers))

@client.event
async def on_server_remove(server):
    await dbl.updateServerCount(len(client.servers))

# Setup background tasks
client.loop.create_task(backgroundTasks.notificationTask(client))
client.loop.create_task(backgroundTasks.reaper(client))

# Run bot
client.run(discordToken)
