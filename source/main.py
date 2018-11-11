"""
Run the bot and start everything
"""

# Things that need importing for logging to be setup
import logging
from modules import struct

# Setup logging (direct logging to file, only log INFO level and above)
# Do this before other imports as some local modules use logging when imported
logFilePath = struct.config["logFilePath"]
handler = logging.FileHandler(filename=logFilePath, encoding="UTF-8", mode="a")
handler.setFormatter(logging.Formatter(struct.config["logFormat"]))
logging.basicConfig(level=logging.INFO, handlers=[handler])
# Change discord to only log ERROR level and above
logging.getLogger("discord").setLevel(logging.ERROR)
# Start logging
logger = logging.getLogger(__name__)
logger.info("Starting bot")

# Import everything else now logging is set up
import discord
from modules import embedGenerators, struct, statics, apis, backgroundTasks                    

# Automaticallu sets up and starts redis connection when imported
from modules.redisClient import redisConn

# Important vars
PREFIX = struct.config["commandPrefix"]
discordToken = struct.loadEnvVar("SpaceXLaunchBotToken")
dblToken = struct.loadEnvVar("dblToken")

class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def on_ready(self):

        # Initialise needed keys with default values if they do not exist
        # Only needed when running for the first time / new db
        if not await redisConn.exists("subscribedChannels"):
            await redisConn.safeSet("subscribedChannels", [], True)
        if not await redisConn.exists("launchNotifSent"):
            await redisConn.safeSet("launchNotifSent", "False")
        if not await redisConn.exists("latestLaunchInfoEmbedDict"):
            await redisConn.safeSet("latestLaunchInfoEmbedDict", statics.generalErrorEmbed, True)

        # Run background tasks after initializing database
        self.loop.create_task(backgroundTasks.notificationTask(self))
        self.loop.create_task(backgroundTasks.reaper(self))

        global dbl  # Can't define this until client (self) is ready
        dbl = apis.dblApiClient(self, dblToken)

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
        logger.info(f"Joined guild, ID: {guild.id}")

    async def on_guild_remove(self, guild):
        await dbl.updateGuildCount(len(self.guilds))
        logger.info(f"Removed from guild, ID: {guild.id}")

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
        

        # Info command

        if message.content.startswith(PREFIX + "nextlaunch"):
            nextLaunchJSON = await apis.spacexAPI.getNextLaunchJSON()
            if nextLaunchJSON == 0:
                launchInfoEmbed, launchInfoEmbedLite = statics.apiErrorEmbed, statics.apiErrorEmbed
            else:
                launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            await self.safeSendLaunchInfo(message.channel, [launchInfoEmbed, launchInfoEmbedLite])


        # Add/remove channel commands

        elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
            # Add channel ID to subbed channels
            replyMsg = "This channel has been added to the launch notification service"

            subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
            if subbedChannelsDict["err"]:
                # return here so nothing else is executed
                return await self.safeSend(message.channel, embed=statics.dbErrorEmbed)

            subbedChannelIDs = subbedChannelsDict["list"]
            if message.channel.id not in subbedChannelIDs:
                subbedChannelIDs.append(message.channel.id)
                ret = await redisConn.safeSet("subscribedChannels", subbedChannelIDs, True)
                if not ret:
                    return await self.safeSend(message.channel, embed=statics.dbErrorEmbed)
            else:
                replyMsg = "This channel is already subscribed to the launch notification service"

            await self.safeSend(message.channel, text=replyMsg)
        
        elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
            # Remove channel ID from subbed channels
            replyMsg = "This channel has been removed from the launch notification service"

            subbedChannelsDict = await redisConn.getSubscribedChannelIDs()
            if subbedChannelsDict["err"]:
                # return here so nothing else is executed
                return await self.safeSend(message.channel, embed=statics.dbErrorEmbed)

            subbedChannelIDs = subbedChannelsDict["list"]
            try:
                # No duplicate elements in the list so remove(value) will always work
                subbedChannelIDs.remove(message.channel.id)
                ret = await redisConn.safeSet("subscribedChannels", subbedChannelIDs, True)
                if not ret:
                    return await self.safeSend(message.channel, embed=statics.dbErrorEmbed)
            except ValueError:
                replyMsg = "This channel was not previously subscribed to the launch notification service"

            await self.safeSend(message.channel, text=replyMsg)


        # Add/remove ping commands

        elif message.content.startswith(PREFIX + "addping"):
            replyMsg: str
            guildID = str(message.guild.id)
            rolesToMention = " ".join(message.content.split("addping")[1:])
            
            if rolesToMention.strip() == "":
                replyMsg = "Invalid input for addping command"
            else:
                replyMsg = f"Added launch notification ping for mentions(s): {rolesToMention}"
                ret = await redisConn.safeSet(guildID, rolesToMention, True)
                if not ret:
                    return await self.safeSend(message.channel, embed=statics.dbErrorEmbed)
                            
            await self.safeSend(message.channel, text=replyMsg)

        elif message.content.startswith(PREFIX + "removeping"):
            guildID = str(message.guild.id)
            ret = await redisConn.delete(guildID)
            if not ret:
                return await self.safeSend(message.channel, text="This server has no pings to be removed")
            await self.safeSend(message.channel, text="Removed ping succesfully")
            

        # Misc

        elif message.content.startswith(PREFIX + "info"):
            await self.safeSend(message.channel, embed=statics.infoEmbed)
        elif message.content.startswith(PREFIX + "help"):
            await self.safeSend(message.channel, embed=statics.helpEmbed)

    async def safeSend(self, channel, text=None, embed=None):
        """
        Send a text / embed message (one or the other, not both) to a
        user, and if an error occurs, safely supress it
        On failure, returns:
            -1 : Nothing to send (text & embed are `None`)
            -2 : Forbidden (API down, Message too big, etc.)
            -3 : HTTPException (No permission to message this channel)
            -4 : InvalidArgument (Invalid channel ID)
        On success returns what the channel.send method returns
        """
        try:
            if text:
                return await channel.send(text)
            elif embed:
                return await channel.send(embed=embed)
            else:
                return -1
        except discord.errors.Forbidden:
            return -2
        except discord.errors.HTTPException:
            return -3
        except discord.errors.InvalidArgument:
            return -4

    async def safeSendLaunchInfo(self, channel, embeds):
        """
        Specifically for sending 2 launch embeds, a full-detail one,
        and failing that, a "lite" version of the embed
        
        parameter $embeds:
            Should be as list of 2 embeds, one to attempt to send,
            and one that is garunteed to be under the character
            limit, to send if the first one is too big.
            It could also be a list with just 1 embed, but if this
            is over the char limit, nothing will happen.
            Other errors are automatically handled
        
        Returns 0 if neither embeds are sent
        """
        for embed in embeds:
            returned = await self.safeSend(channel, embed=embed)
            if returned == -3:
                pass  # Embed might be too big, try lite version
            elif returned == -2 or returned == -4:
                return 0
            else:
                return returned
        # Both failed to send, try to let user know something went wrong
        await self.safeSend(channel, embed=statics.generalErrorEmbed)
        return 0

# Run bot
client = SpaceXLaunchBotClient()
client.run(discordToken)
