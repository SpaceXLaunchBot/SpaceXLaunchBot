import logging
from typing import Union

import discord

import apis
import commands
import config
import notifications
import statics
from sqlitedb import sqlitedb


class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        logging.info("Client initialised")

        # Create asyncio tasks now
        self.loop.create_task(notifications.notification_task(self))

    async def on_ready(self) -> None:
        logging.info("Successfully connected to Discord API")
        await self.set_playing(config.BOT_GAME)
        await self.update_website_metrics()

    async def shutdown(self):
        logging.info("Shutting down")
        sqlitedb.stop()
        await self.logout()

    async def update_website_metrics(self) -> None:
        """Update Discord bot websites with guild count"""
        gc = len(self.guilds)
        logging.info(f"Updating bot lists with a guild_count of {gc}")
        await apis.bot_lists.post_all_bot_lists(gc)

    async def on_guild_join(self, guild: discord.guild) -> None:
        logging.info(f"Joined guild, ID: {guild.id}")
        await self.update_website_metrics()

    async def on_guild_remove(self, guild: discord.guild) -> None:
        logging.info(f"Removed from guild, ID: {guild.id}")
        await self.update_website_metrics()

        deleted = sqlitedb.delete_guild_mentions(guild.id)
        if deleted != 0:
            logging.info(f"Removed guild settings for {guild.id}")

    async def set_playing(self, title: str) -> None:
        """Set the bots current "Playing: " status.

        Args:
            title: The title of the "game" the bot is playing.

        """
        await self.change_presence(activity=discord.Game(name=title))

    async def on_message(self, message: discord.message) -> None:
        if message.author.bot or not message.guild:
            return

        message_parts = message.content.lower().split(" ")

        # ToDo: Temporary, remove after n months
        if message_parts[0].startswith(config.BOT_COMMAND_PREFIX_LEGACY):
            if message_parts[0][1:] in commands.CMD_LOOKUP:
                await self.send_s(message.channel, statics.LEGACY_PREFIX_WARNING_EMBED)
            return

        if message_parts[0] != config.BOT_COMMAND_PREFIX:
            return

        command_used = message_parts[1]

        try:
            run_command = commands.CMD_LOOKUP[command_used]
            # All commands are passed the client and the message objects
            to_send = await run_command(client=self, message=message)

        except KeyError:
            to_send = None

        if to_send is None:
            return

        await self.send_s(message.channel, to_send)

    @staticmethod
    async def send_s(
        channel: discord.TextChannel, to_send: Union[str, discord.Embed]
    ) -> int:
        """Sends a text / embed message to a channel safely.

        If an error occurs, safely suppress it so the bot doesn't crash.

        Args:
            channel: A discord.Channel object.
            to_send: A String or discord.Embed object.

        Returns:
            An integer 0 to -4:
                 0 : Success
                -1 : Message / embed / embed.title too long.
                -2 : Nothing to send (to_send is not a string or Embed).
                -3 : Forbidden (No permission to message this channel).
                -4 : HTTPException (API down, network issues, etc.).

        """
        # ToDo: These return codes aren't actually used for anything yet
        try:
            if isinstance(to_send, str):
                if len(to_send) > 2000:
                    return -1
                await channel.send(to_send)
                return 0
            if isinstance(to_send, discord.Embed):
                if len(to_send) > 2048 or len(to_send.title) > 256:
                    return -1
                await channel.send(embed=to_send)
                return 0
            return -2
        except discord.errors.Forbidden:
            return -3
        except discord.errors.HTTPException:
            return -4

    async def send_all_subscribed(
        self, to_send: Union[str, discord.Embed], send_mentions: bool = False
    ) -> None:
        """Send a message to all subscribed channels.

        Args:
            to_send: A String or discord.Embed object.
            send_mentions: If True, get mentions from db and send as well.

        """
        channel_ids = sqlitedb.get_subbed_channels()
        invalid_ids = set()

        for channel_id in channel_ids:
            channel = self.get_channel(channel_id)

            if channel is None:
                invalid_ids.add(channel_id)
                continue

            await self.send_s(channel, to_send)

            if send_mentions:
                mentions = sqlitedb.get_guild_mentions(channel.guild.id)
                if mentions != "":
                    await self.send_s(channel, mentions)

        # Remove any channels from db that are picked up as invalid
        sqlitedb.remove_subbed_channels(invalid_ids)
