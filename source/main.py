import logging
from modules import structure  # Import this before to set up logging

logger = logging.getLogger(__name__)
logger.info("Starting bot")

import discord, asyncio
from aredis import RedisError

from modules import embedGenerators, statics, apis, backgroundTasks
from modules.redisClient import redisConn

PREFIX = structure.config["commandPrefix"]
DISCORD_TOKEN = structure.loadEnvVar("SpaceXLaunchBotToken")
DBL_TOKEN = structure.loadEnvVar("dblToken")


class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_tasks_started = False
        logger.info("SpaceXLaunchBotClient initialised")

    async def on_ready(self):
        global dbl
        dbl = apis.dblApi(self, DBL_TOKEN)

        # Only needed when running for the first time / new db
        if not await redisConn.exists("notificationTaskStore"):
            logger.info("notificationTaskStore does not exist, creating")
            await redisConn.setNotificationTaskStore("False", statics.generalErrorEmbed)

        """
        11/04/19
          - BG / NOTIF TASKS DISABLED DUE TO SPAM (unknown reason)
        13/04/19
          - Quick fix for spam (will be properly fixed in bg-tasks-rewrite branch)
          - I am fairly certain the issue was that the on_ready method was called if the
            client recconnected, which meant that these tasks kept getting duplicated
        """
        if self.bg_tasks_started == False:
            logger.info("self.bg_tasks_started is False, startings tasks")
            # These will actually work without passing the 3 Nones, as the wrapper for the functions
            # deals with those 3 arguments. None is used just so editors / linters won't show errors
            self.loop.create_task(
                backgroundTasks.launchingSoonNotifTask(self, None, None, None)
            )
            self.loop.create_task(
                backgroundTasks.launchChangedNotifTask(self, None, None, None)
            )
            self.bg_tasks_started = True

        await self.change_presence(activity=discord.Game(name=structure.config["game"]))

        totalSubbed = await redisConn.scard("subscribedChannels")
        totalGuilds = len(self.guilds)
        logger.info(f"{self.user.id} / {self.user.name}")
        logger.info(
            f"{totalGuilds} guilds / {totalSubbed} subscribed channels / {len(self.users)} users"
        )
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

        # If the command fails, the bot should keep running, but log the error
        try:
            await self.handleCommand(message, userIsOwner, userIsAdmin)
        except RedisError as e:
            logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
            await self.safeSend(message.channel, statics.dbErrorEmbed)
        except Exception as e:
            logger.error(f"handleCommand failed:  {type(e).__name__}: {e}")
            await self.safeSend(message.channel, statics.generalErrorEmbed)

    async def handleCommand(self, message, userIsOwner, userIsAdmin):

        # Info command

        if message.content.startswith(PREFIX + "nextlaunch"):
            nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON()
            if nextLaunchJSON == -1:
                launchInfoEmbed = statics.apiErrorEmbed
            else:
                launchInfoEmbed = await embedGenerators.genLaunchInfoEmbeds(
                    nextLaunchJSON
                )
            await self.safeSend(message.channel, launchInfoEmbed)

        # Add/remove channel commands

        # elif userIsAdmin and message.content.startswith(PREFIX + "addchannel"):
        #     reply = "This channel has been added to the notification service"
        #     added = await redisConn.sadd(
        #         "subscribedChannels", str(message.channel.id).encode("UTF-8")
        #     )
        #     if added == 0:
        #         reply = "This channel is already subscribed to the notification service"
        #     await self.safeSend(message.channel, reply)

        # elif userIsAdmin and message.content.startswith(PREFIX + "removechannel"):
        #     reply = "This channel has been removed from the launch notification service"
        #     removed = await redisConn.srem(
        #         "subscribedChannels", str(message.channel.id).encode("UTF-8")
        #     )
        #     if removed == 0:
        #         reply = "This channel was not previously subscribed to the launch notification service"
        #     await self.safeSend(message.channel, reply)

        # Add/remove ping commands

        # elif userIsAdmin and message.content.startswith(PREFIX + "addping"):
        #     reply = "Invalid input for addping command"
        #     rolesToMention = " ".join(message.content.split("addping")[1:])
        #     if rolesToMention.strip() != "":
        #         reply = (
        #             f"Added launch notification ping for mentions(s): {rolesToMention}"
        #         )
        #         await redisConn.setGuildSettings(message.guild.id, rolesToMention)
        #     await self.safeSend(message.channel, reply)

        # elif userIsAdmin and message.content.startswith(PREFIX + "removeping"):
        #     reply = "Removed ping succesfully"
        #     deleted = await redisConn.hdel(message.guild.id, "rolesToMention")
        #     if deleted == 0:
        #         reply = "This server has no pings to be removed"
        #     await self.safeSend(message.channel, reply)

        # Misc

        elif message.content.startswith(PREFIX + "info"):
            await self.safeSend(message.channel, statics.infoEmbed)
        elif message.content.startswith(PREFIX + "help"):
            await self.safeSend(message.channel, statics.helpEmbed)

        # Debugging

        elif userIsOwner and message.content.startswith(PREFIX + "dbgls"):
            # DeBugLaunchingSoon - Send launching soon embed for prev launch
            nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON(debug=True)
            lse = await embedGenerators.genLaunchingSoonEmbed(nextLaunchJSON)
            await self.safeSend(message.channel, lse)

        elif userIsOwner and message.content.startswith(PREFIX + "resetnts"):
            # Reset notificationTaskStore to default values (triggers notifications)
            await redisConn.setNotificationTaskStore("False", statics.generalErrorEmbed)
            await self.safeSend(message.channel, "Reset notificationTaskStore")

    async def safeSend(self, channel, toSend):
        """
        Send a text / embed message to a user, and if an error occurs, safely
        supress it so the bot doesen't crash completely. On failure, returns:
            -1 : Nothing to send (toSend is not a string or Embed)
            -2 : Forbidden (No permission to message this channel)
            -3 : HTTPException (API down, Message too big, etc.)
            -4 : InvalidArgument (Invalid channel ID / cannot "see" that channel)
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


# Run bot
client = SpaceXLaunchBotClient()
client.run(DISCORD_TOKEN)
