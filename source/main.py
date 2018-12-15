import logging
logger = logging.getLogger(__name__)
logger.info("Starting bot")

import discord
from modules import structure, embedGenerators, statics, apis, backgroundTasks
from modules.redisClient import redisConn

PREFIX = structure.config["commandPrefix"]
DISCORD_TOKEN = structure.loadEnvVar("SpaceXLaunchBotToken")
DBL_TOKEN = structure.loadEnvVar("dblToken")

class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def on_ready(self):
        global dbl
        dbl = apis.dblApiClient(self, DBL_TOKEN)
 
        # Only needed when running for the first time / new db
        if not await redisConn.exists("notificationTaskStore"):
            logger.info("notificationTaskStore does not exist in Redis, creating")
            await redisConn.setNotificationTaskStore("False", statics.generalErrorEmbed)

        # Run background tasks after initializing database
        self.loop.create_task(backgroundTasks.notificationTask(self))

        await self.change_presence(activity=discord.Game(name=structure.config["game"]))

        totalSubbed = await redisConn.scard("subscribedChannels")
        totalGuilds = len(self.guilds)
        
        logger.info(f"{self.user.id} / {self.user.name}")
        logger.info(f"{totalGuilds} guilds / {totalSubbed} subscribed channels / {len(self.users)} users")
        logger.info("Bot ready")

        await dbl.updateGuildCount(totalGuilds)

    async def on_guild_join(self, guild):
        await dbl.updateGuildCount(len(self.guilds))
        logger.info(f"Joined guild, ID: {guild.id}")

    async def on_guild_remove(self, guild):
        # TODO: Check if guild settings exist, if so, delete from db (and log the fact a deletion occured)
        await dbl.updateGuildCount(len(self.guilds))
        logger.info(f"Removed from guild, ID: {guild.id}")

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            # Don't reply to bots (includes self)
            # Don't reply to PM's
            # TODO: Only reply in textChannel instances
            return

        try:
            userIsAdmin = message.author.permissions_in(message.channel).administrator
        except AttributeError:
            userIsAdmin = False  # If user has no roles

        # Commands can be in any case
        message.content = message.content.lower()
        

        # Info command

        if message.content.startswith(PREFIX + "nextlaunch"):
            nextLaunchJSON = await apis.spacexAPI.getNextLaunchJSON()
            if nextLaunchJSON == -1:
                launchInfoEmbed, launchInfoEmbedLite = statics.apiErrorEmbed, statics.apiErrorEmbed
            else:
                launchInfoEmbed, launchInfoEmbedLite = await embedGenerators.getLaunchInfoEmbed(nextLaunchJSON)
            await self.safeSendLaunchInfo(message.channel, [launchInfoEmbed, launchInfoEmbedLite])


        # Add/remove channel commands

        elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
            replyMsg = "This channel has been added to the notification service"
            ret = await redisConn.safeSadd("subscribedChannels", str(message.channel.id))
            if ret == 0:
                replyMsg = "This channel is already subscribed to the notification service"
            elif ret == -1:
                return await self.safeSend(message.channel, statics.dbErrorEmbed)
            await self.safeSend(message.channel, replyMsg)
        
        elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
            replyMsg = "This channel has been removed from the launch notification service"
            ret = await redisConn.srem("subscribedChannels", str(message.channel.id).encode("UTF-8"))
            if ret == 0:
                replyMsg = "This channel was not previously subscribed to the launch notification service"
            elif ret == -1:
                return await self.safeSend(message.channel, statics.dbErrorEmbed)
            await self.safeSend(message.channel, replyMsg)


        # Add/remove ping commands

        elif message.content.startswith(PREFIX + "addping"):
            replyMsg = "Invalid input for addping command"
            rolesToMention = " ".join(message.content.split("addping")[1:])
            if rolesToMention.strip() != "":
                replyMsg = f"Added launch notification ping for mentions(s): {rolesToMention}"
                ret = await redisConn.setGuildSettings(message.guild.id, rolesToMention)
                if ret == -1:
                    return await self.safeSend(message.channel, statics.dbErrorEmbed)
            await self.safeSend(message.channel, replyMsg)

        elif message.content.startswith(PREFIX + "removeping"):
            """
            Currently just deletes the guild settings Redis key/val as the only setting saved is the mentionsToPing
            TODO: Once we are storing more per-guild settings, don't delete the whole key here
            """
            ret = await redisConn.delete(str(message.guild.id))
            if ret == 0:
                # ret is the number of keys deleted
                return await self.safeSend(message.channel, "This server has no pings to be removed")
            await self.safeSend(message.channel, "Removed ping succesfully")
            

        # Misc

        elif message.content.startswith(PREFIX + "info"):
            await self.safeSend(message.channel, statics.infoEmbed)
        elif message.content.startswith(PREFIX + "help"):
            await self.safeSend(message.channel, statics.helpEmbed)

    async def safeSend(self, channel, toSend):
        """
        Send a text / embed message to a user, and if an error occurs, safely
        supress it. On failure, returns:
            -1 : Nothing to send (toSend is not a string or Embed)
            -2 : Forbidden (API down, Message too big, etc.)
            -3 : HTTPException (No permission to message this channel)
            -4 : InvalidArgument (Invalid channel ID)
        On success returns what the channel.send method returns
        """
        try:
            if type(toSend) == str:
                return await channel.send(toSend)
            elif type(toSend) == discord.Embed:
                return await channel.send(embed=toSend)
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
            returned = await self.safeSend(channel, embed)
            if returned == -3:
                pass  # Embed might be too big, try lite version
            elif returned == -2 or returned == -4:
                return 0
            else:
                return returned
        # Both failed to send, try to let user know something went wrong
        await self.safeSend(channel, statics.generalErrorEmbed)
        return 0

# Run bot
client = SpaceXLaunchBotClient()
client.run(DISCORD_TOKEN)
