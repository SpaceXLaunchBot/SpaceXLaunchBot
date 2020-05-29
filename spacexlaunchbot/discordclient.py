import logging
import platform
import signal
import sys
from typing import Union

import discord
import discordhealthcheck

import apis
import commands
import config
import notifications
import statics
import storage


class SpaceXLaunchBotClient(discord.Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        logging.info("Client initialised")

        self.ds = storage.DataStore(config.PICKLE_DUMP_LOCATION)
        logging.info("Data storage initialised")

        if platform.system() == "Linux":
            self.loop.add_signal_handler(
                signal.SIGTERM, lambda: self.loop.create_task(self.shutdown())
            )
            logging.info("Signal handler for SIGTERM registered")

        # Create asyncio tasks now
        self.loop.create_task(notifications.notification_task(self))
        discordhealthcheck.start(self)

    async def on_ready(self) -> None:
        logging.info("Connected to Discord API")
        await self.set_playing(config.BOT_GAME)
        await self.update_website_metrics()

    async def shutdown(self) -> None:
        # ToDo: Shutdown all tasks
        logging.info("Shutting down")
        self.ds.save()
        await self.close()

    async def update_website_metrics(self) -> None:
        """Update Discord bot websites with guild count"""
        guild_count = len(self.guilds)
        logging.info(f"Updating bot lists with a guild_count of {guild_count}")
        await apis.bot_lists.post_all_bot_lists(guild_count)

    async def on_guild_join(self, guild: discord.guild) -> None:
        logging.info(f"Joined guild, ID: {guild.id}")
        await self.update_website_metrics()

    async def on_guild_remove(self, guild: discord.guild) -> None:
        logging.info(f"Removed from guild, ID: {guild.id}")
        await self.update_website_metrics()

        if self.ds.remove_guild_options(guild.id) is True:
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
                await self._send_s(message.channel, statics.LEGACY_PREFIX_WARNING_EMBED)
            return

        if message_parts[0] != config.BOT_COMMAND_PREFIX:
            return

        command_used = message_parts[1]

        to_send = None

        try:
            run_command = commands.CMD_LOOKUP[command_used]
            # All commands are passed the client and the message objects
            to_send = await run_command(client=self, message=message)

        except KeyError:
            pass

        except TypeError:
            logging.exception(f"to_send failed, {command_used=}, {message.content=}")

        if to_send is None:
            return

        await self._send_s(message.channel, to_send)

    @staticmethod
    async def _send_s(
        channel: discord.TextChannel, to_send: Union[str, discord.Embed]
    ) -> None:
        """Safely send a text / embed message to a channel. Logs any errors that occur.

        Args:
            channel: A discord.Channel object.
            to_send: A String or discord.Embed object.

        """
        try:
            if isinstance(to_send, str):
                if len(to_send) > 2000:
                    logging.warning("Failed to send message: len of to_send > 2000")
                else:
                    await channel.send(to_send)

            elif isinstance(to_send, discord.Embed):
                if len(to_send) > 2048 or len(to_send.title) > 256:
                    logging.warning("Failed to send message: len of embed too long")
                else:
                    await channel.send(embed=to_send)

        except (discord.errors.Forbidden, discord.errors.HTTPException):
            ex, val, _ = sys.exc_info()
            if ex is not None:  # MyPy must be pleased.
                logging.warning(f"Failed to send message: {ex.__name__}: {val}")

    async def send_all_subscribed(
        self, to_send: Union[str, discord.Embed], send_mentions: bool = False
    ) -> None:
        """Send a message to all subscribed channels.

        Args:
            to_send: A String or discord.Embed object.
            send_mentions: If True, get mentions from db and send as well.

        """
        channel_ids = self.ds.get_subbed_channels()
        guild_opts = self.ds.get_all_guilds_options()
        invalid_ids = set()

        for channel_id in channel_ids:
            channel = self.get_channel(channel_id)

            if channel is None:
                invalid_ids.add(channel_id)
                continue

            await self._send_s(channel, to_send)

            if send_mentions:
                if (opts := guild_opts.get(channel.guild.id)) is not None:
                    if (mentions := opts.get("mentions")) is not None:
                        await self._send_s(channel, mentions)

        # Remove any channels from db that are picked up as invalid
        self.ds.remove_subbed_channels(invalid_ids)
