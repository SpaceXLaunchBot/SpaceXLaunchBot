"""
Run the bot and start everything
"""

# Built-ins and 3rd party modules
import logging
import discord
from os import path

# Setup logging stuff
from modules import logSetup
logSetup.setup()

# Setup and start redis connection
from modules import redisClient
redisConn = redisClient.startRedisConnection()

# Import everything else (once logging is set up)
from modules import fs, utils, errors, dblAPI, spacexAPI, staticMessages, embedGenerators, backgroundTasks
from modules.discordUtils import safeSend, safeSendLaunchInfo

logger = logging.getLogger(__name__)
logger.info("Starting bot")

# Important vars
PREFIX = fs.config["commandPrefix"]
discordToken = utils.loadEnvVar("SpaceXLaunchBotToken")

class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Setup background tasks
        # Will func(self) work?
        self.loop.create_task(backgroundTasks.notificationTask(self))
        self.loop.create_task(backgroundTasks.reaper(self))
    
    async def on_ready(self):
        global dbl  # Can't define this until client is ready
        dbl = dblAPI.dblClient(self)

        await self.change_presence(activity=discord.Game(name="with rockets"))

        subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
        totalSubbed = len(subbedChannelsDict["list"])
        totalGuilds = len(self.guilds)
        totalUsers = len(self.users)   
        
        logger.info(f"Username: {self.user.name}")
        logger.info(f"ClientID: {self.user.id}")
        logger.info(f"Connected to {totalGuilds} guilds")
        logger.info(f"Connected to {totalSubbed} subscribed channels")
        logger.info(f"Serving {totalUsers} users")
        logger.info("Bot ready")

        await dbl.updateGuildCount(totalGuilds)

    async def on_guild_join(self, guild):
        await dbl.updateGuildCount(len(self.guilds))

    async def on_guild_remove(self, guild):
        await dbl.updateGuildCount(len(self.guilds))

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            # Don't reply to bots (includes self)
            # Don't reply to PM's
            return

        try:
            userIsAdmin = message.author.permissions_in(message.channel).administrator
        except AttributeError:
            # Happens if user has no roles
            userIsAdmin = False

        # Commands can be in any case
        message.content = message.content.lower()
        

        if message.content.startswith(PREFIX + "nextlaunch"):
            nextLaunchJSON = await spacexAPI.getNextLaunchJSON()
            if nextLaunchJSON == 0:
                launchInfoEmbed, launchInfoEmbedLite = errors.apiErrorEmbed, errors.apiErrorEmbed
            else:
                launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            await safeSendLaunchInfo(message.channel, [launchInfoEmbed, launchInfoEmbedLite])


        # Add/remove channel commands

        elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
            # Add channel ID to subbed channels
            replyMsg = "This channel has been added to the launch notification service"

            subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
            if subbedChannelsDict["err"]:
                # return here so nothing else is executed
                return await safeSend(message.channel, embed=errors.dbErrorEmbed)

            subbedChannelIDs = subbedChannelsDict["list"]
            if message.channel.id not in subbedChannelIDs:
                subbedChannelIDs.append(message.channel.id)
                ret = await redisConn.safeSet("subscribedChannels", subbedChannelIDs, True)
                if not ret:
                    return await safeSend(message.channel, embed=errors.dbErrorEmbed)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"

            await safeSend(message.channel, text=replyMsg)
        
        elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
            # Remove channel ID from subbed channels
            replyMsg = "This channel has been removed from the launch notification service"

            subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
            if subbedChannelsDict["err"]:
                # return here so nothing else is executed
                return await safeSend(message.channel, embed=errors.dbErrorEmbed)

            subbedChannelIDs = subbedChannelsDict["list"]
            try:
                # No duplicate elements in the list so remove(value) will always work
                subbedChannelIDs.remove(message.channel.id)
                ret = await redisConn.safeSet("subscribedChannels", subbedChannelIDs, True)
                if not ret:
                    return await safeSend(message.channel, embed=errors.dbErrorEmbed)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"

            await safeSend(message.channel, text=replyMsg)


        # Add/remove ping commands

        elif message.content.startswith(PREFIX + "addping"):
            replyMsg: str
            guildID = str(message.guild.id)
            rolesToMention = " ".join(message.content.split("addping")[1:])
            
            if rolesToMention.strip() == "":
                replyMsg = "Invalid input for addPing command"
            else:
                replyMsg = f"Added ping for tag(s): {rolesToMention}"
                ret = await redisConn.safeSet(guildID, rolesToMention, True)
                if not ret:
                    return await safeSend(message.channel, embed=errors.dbErrorEmbed)
            
            await safeSend(message.channel, text=replyMsg)

        elif message.content.startswith(PREFIX + "removeping"):
            guildID = str(message.guild.id)
            ret = await redisConn.delete(guildID)
            if not ret:
                # TODO: Word this better
                return await safeSend(message.channel, text="No pings were found to be removed")
            await safeSend(message.channel, text="Removed ping succesfully")
            

        # Misc

        elif message.content.startswith(PREFIX + "info"):
            await safeSend(message.channel, embed=staticMessages.infoEmbed)
        elif message.content.startswith(PREFIX + "help"):
            await safeSend(message.channel, embed=staticMessages.helpEmbed)

# Run bot
client = SpaceXLaunchBotClient()
client.run(discordToken)
