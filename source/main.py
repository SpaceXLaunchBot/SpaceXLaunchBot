# Built-ins and 3rd party modules
from os import path
import discord
import logging

# Local modules
from modules import fs, utils, errors, dblAPI, spacexAPI, staticMessages, embedGenerators, backgroundTasks
from modules.discordUtils import safeSend, safeSendLaunchInfo

# Setup logging
logFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "bot.log")
handler = logging.FileHandler(filename=logFilePath, encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(funcName)s: %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Change discord to only log warnings and above
logging.getLogger("discord").setLevel(logging.WARNING)

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
    
    logger.info("Username: {}".format(client.user.name))
    logger.info("ClientID: {}".format(client.user.id))
    logger.info("Connected to {} servers".format(totalServers))
    logger.info("Connected to {} subscribed channels".format(totalSubbed))
    logger.info("Serving {} clients".format(totalClients))

    await dbl.updateServerCount(totalServers)

    print("Bot loaded and running")

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
