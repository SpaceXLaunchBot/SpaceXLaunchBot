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
            logger.info("notificationTaskStore does not exist, creating")
            await redisConn.setNotificationTaskStore("False", statics.generalErrorEmbed)
        
        self.loop.create_task(backgroundTasks.notificationTask(self))

        await self.change_presence(activity=discord.Game(name=structure.config["game"]))

        totalSubbed = await redisConn.scard("subscribedChannels")
        totalGuilds = len(self.guilds)        
        logger.info(f"{self.user.id} / {self.user.name}")
        logger.info(f"{totalGuilds} guilds / {totalSubbed} subscribed channels / {len(self.users)} users")
        logger.info("Bot ready")

        await dbl.updateGuildCount(totalGuilds)

    async def on_guild_join(self, guild):
        logger.info(f"Joined guild, ID: {guild.id}")
        await dbl.updateGuildCount(len(self.guilds))

    async def on_guild_remove(self, guild):
        logger.info(f"Removed from guild, ID: {guild.id}")
        await dbl.updateGuildCount(len(self.guilds))
        deleted = await redisConn.delete(str(guild.id))
        if deleted != 0:
            logger.info(f"Removed server settings for {guild.id}")

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            # Don't reply to bots (includes self)
            # Only reply to messages from guilds
            return

        userIsOwner = message.author.id == int(structure.config["ownerID"])
        try:
            userIsAdmin = message.author.permissions_in(message.channel).administrator
        except AttributeError:
            userIsAdmin = False  # If user has no roles

        # Commands can be in any case
        message.content = message.content.lower()
        

        # Info command

        if message.content.startswith(PREFIX + "nextlaunch"):
            nextLaunchJSON = await apis.spacexAPI.getNextLaunchJSON()
            launchInfoEmbed, launchInfoEmbedSmall = await embedGenerators.genLaunchInfoEmbeds(nextLaunchJSON)
            await self.safeSendLaunchInfo(message.channel, launchInfoEmbed, launchInfoEmbedSmall)


        # Add/remove channel commands

        elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
            reply = "This channel has been added to the notification service"
            added = await redisConn.safeSadd("subscribedChannels", str(message.channel.id))
            if added == 0:
                reply = "This channel is already subscribed to the notification service"
            elif added == -1:
                reply = statics.dbErrorEmbed
            await self.safeSend(message.channel, reply)
        
        elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
            reply = "This channel has been removed from the launch notification service"
            removed = await redisConn.srem("subscribedChannels", str(message.channel.id).encode("UTF-8"))
            if removed == 0:
                reply = "This channel was not previously subscribed to the launch notification service"
            elif removed == -1:
                reply = statics.dbErrorEmbed
            await self.safeSend(message.channel, reply)


        # Add/remove ping commands

        elif userIsAdmin and message.content.startswith(PREFIX + "addping"):
            reply = "Invalid input for addping command"
            rolesToMention = " ".join(message.content.split("addping")[1:])
            if rolesToMention.strip() != "":
                reply = f"Added launch notification ping for mentions(s): {rolesToMention}"
                ret = await redisConn.setGuildSettings(message.guild.id, rolesToMention)
                if ret == -1:
                    return await self.safeSend(message.channel, statics.dbErrorEmbed)
            await self.safeSend(message.channel, reply)

        elif userIsAdmin and message.content.startswith(PREFIX + "removeping"):
            deleted = await redisConn.hdel(message.guild.id, "rolesToMention")
            if deleted == 0:
                return await self.safeSend(message.channel, "This server has no pings to be removed")
            await self.safeSend(message.channel, "Removed ping succesfully")
            

        # Misc

        elif message.content.startswith(PREFIX + "info"):
            await self.safeSend(message.channel, statics.infoEmbed)
        elif message.content.startswith(PREFIX + "help"):
            await self.safeSend(message.channel, statics.helpEmbed)
        

        # Debugging

        elif userIsOwner and message.content.startswith(PREFIX + "dbgls"):
            # Send launching soon embed
            nextLaunchJSON = await apis.spacexAPI.getNextLaunchJSON(debug=True)
            if nextLaunchJSON == -1:
                return await self.safeSend(message.channel, statics.apiErrorEmbed)
            lse = await embedGenerators.genLaunchingSoonEmbed(nextLaunchJSON)
            await self.safeSend(message.channel, lse)


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

    async def safeSendLaunchInfo(self, channel, launchInfoEmbed, launchInfoEmbedSmall, sendErr=True):
        """
        Safely send the launch information embed. If this fails, send the
        smaller version that should always be under the character limit for an
        embed, failing this, send an error message (if sendErr=True)
        """
        sent = await self.safeSend(channel, launchInfoEmbed)

        if sent in [-2, -3]:
            # Launch embed might be too big, try smaller version
            sent = await self.safeSend(channel, launchInfoEmbedSmall)

            if sent in [-2, -3] and sendErr:
                # Still something wrong, try to send error embed
                await self.safeSend(channel, statics.generalErrorEmbed)

# Run bot
client = SpaceXLaunchBotClient()
client.run(DISCORD_TOKEN)
