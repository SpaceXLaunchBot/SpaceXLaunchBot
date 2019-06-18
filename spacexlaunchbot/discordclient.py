import discord
import logging

import commands
import bgtasks
import apis
import config
from redisclient import REDIS


class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.info("Client initialised")

        # Create asyncio tasks now
        self.loop.create_task(bgtasks.notification_task(self))

    async def on_ready(self):
        logging.info("Successfully connected to Discord API")
        await self.set_playing(config.BOT_GAME)
        await apis.dbl.update_guild_count(len(self.guilds))

    async def on_guild_join(self, guild):
        logging.info(f"Joined guild, ID: {guild.id}")
        await apis.dbl.update_guild_count(len(self.guilds))

    async def on_guild_remove(self, guild):
        logging.info(f"Removed from guild, ID: {guild.id}")
        await apis.dbl.update_guild_count(len(self.guilds))

        deleted = await REDIS.delete_guild_mentions(guild.id)
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

    @staticmethod
    async def safe_send(channel, to_send):
        """Sends a text / embed message to a channel
        If an error occurs, safely suppress it so the bot doesn't crash
        On success returns what the channel.send method returns
        On failure, returns:
         -1 : Message / embed / embed.title too long
         -2 : Nothing to send (to_send is not a string or Embed)
         -3 : Forbidden (No permission to message this channel)
         -4 : HTTPException (API down, network issues, etc.)
        """
        try:
            if isinstance(to_send, str):
                if len(to_send) > 2000:
                    return -1
                return await channel.send(to_send)
            if isinstance(to_send, discord.Embed):
                if len(to_send) > 2048 or len(to_send.title) > 256:
                    return -1
                return await channel.send(embed=to_send)
            return -2
        except discord.errors.Forbidden:
            return -3
        except discord.errors.HTTPException:
            return -4

    async def set_watching(self, title):
        await self.change_presence(
            activity=discord.Activity(name=title, type=discord.ActivityType.watching)
        )

    async def set_playing(self, title):
        await self.change_presence(activity=discord.Game(name=title))
