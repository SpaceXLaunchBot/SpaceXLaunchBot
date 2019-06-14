import discord
import logging

import commands
import bgtasks
import apis
import config
from redisclient import redis


class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.info("Client initialised")

        # Create asyncio tasks now
        self.loop.create_task(bgtasks.notification_task(self))

    async def on_ready(self):
        logging.info("Successfully connected to Discord API")

        self.dbl = apis.dbl.DblApi(self.user.id, config.API_TOKEN_DBL)

        await self.change_presence(activity=discord.Game(name=config.BOT_GAME))
        await self.dbl.update_guild_count(len(self.guilds))

    async def on_guild_join(self, guild):
        logging.info(f"Joined guild, ID: {guild.id}")
        await self.dbl.update_guild_count(len(self.guilds))

    async def on_guild_remove(self, guild):
        logging.info(f"Removed from guild, ID: {guild.id}")
        await self.dbl.update_guild_count(len(self.guilds))

        deleted = await redis.delete_guild_mentions(guild.id)
        if deleted != 0:
            logging.info(f"Removed guild settings for {guild.id}")

    async def on_message(self, message):
        if (
            not message.content.startswith(config.BOT_COMMAND_PREFIX)
            or message.author.bot
            or not message.guild
        ):
            # Not possibly a command (doesn't start with prefix)
            # Don't reply to bots (includes self)
            # Only reply to messages from guilds
            return
        await commands.handle_command(self, message)

    async def safe_send(self, channel, to_send):
        """Sends a text / embed message to a channel
        If an error occurs, safely supress it so the bot doesen't crash
        On success returns what the channel.send method returns
        On failure, returns:
         -1 : Message / embed too big
         -2 : Nothing to send (to_send is not a string or Embed)
         -3 : Forbidden (No permission to message this channel)
         -4 : HTTPException (API down, network issues, etc.)
         -5 : InvalidArgument (Invalid channel --> cannot "see" that channel)
        """
        try:
            if type(to_send) == str:
                if len(to_send) > 2000:
                    return -1
                return await channel.send(to_send)
            elif type(to_send) == discord.Embed:
                if len(to_send) > 2048 or len(to_send.title) > 256:
                    return -1
                return await channel.send(embed=to_send)
            else:
                return -2
        except discord.errors.Forbidden:
            return -3
        except discord.errors.HTTPException:
            return -4
        except discord.errors.InvalidArgument:
            return -5
