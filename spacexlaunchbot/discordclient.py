import asyncio
import logging
import platform
import signal
from typing import Union

import discord
import discordhealthcheck

from . import apis
from . import commands
from . import config
from . import embeds
from . import storage
from .notifications import start_notification_loop, NotificationType
from .utils import sys_info


class SpaceXLaunchBotClient(discord.Client):
    # The signals package is a bit iffy when it comes to pylint.
    # See https://github.com/PyCQA/pylint/issues/2804
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.info("Client initialised")
        logging.info(sys_info())

        if platform.system() != "Windows":
            signals = (
                signal.SIGHUP,
                signal.SIGTERM,
                signal.SIGINT,
                signal.SIGQUIT,
            )
            logging.info("Not on Windows, registering signal handlers")
            for s in signals:
                self.loop.add_signal_handler(
                    s, lambda sig=s: self.loop.create_task(self.shutdown(sig=sig))
                )

        self.ds = storage.DataStore(
            self.loop,
            config.PICKLE_DUMP_LOCATION,
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
        )
        logging.info("Data storage initialised")

        self.notification_task = self.loop.create_task(start_notification_loop(self))
        self.healthcheck_server = discordhealthcheck.start(self)

        self.dc_logger: Union[asyncio.Task, None] = None

    @property
    def latency_ms(self) -> int:
        """Converts the latency property to an int representing the value in ms."""
        return int(self.latency * 1000)

    async def on_connect(self) -> None:
        logging.info(f"Connected to Discord API with a latency of {self.latency_ms}ms")

    async def on_disconnect(self) -> None:
        # Wait 2 seconds, if we don't reconnect, log it.
        self.dc_logger = self.loop.create_task(self.disconnected_logger())

    @staticmethod
    async def disconnected_logger() -> None:
        """Sleep for 2 seconds then log a disconnect."""
        # NOTE: The whole reason for this function is so that the on_resumed method can
        # cancel this function running as a task, this prevents the log filling up with
        # reconnection logs.
        try:
            await asyncio.sleep(2)
            logging.info("Disconnected from Discord API")
        except asyncio.CancelledError:
            pass

    async def on_resumed(self) -> None:
        if self.dc_logger is None:
            return  # Hmm

        if not self.dc_logger.done():
            # We're within the 2 seconds, cancel it and log nothing
            self.dc_logger.cancel()
            return

        logging.info(
            f"Resumed connection to Discord API with a latency of {self.latency_ms}ms"
        )

    async def on_ready(self) -> None:
        logging.info("Client ready")
        await self.set_playing(config.BOT_GAME_NAME)
        await self.update_website_metrics()

    async def shutdown(self, sig: signal.Signals = None) -> None:
        """Disconnects from Discord and cancels asyncio tasks"""
        logging.info("Shutdown called")

        if sig is not None:
            logging.info(f"Shutdown due to signal: {sig.name}")

        logging.info("Cancelling notification_task")
        self.notification_task.cancel()
        await self.notification_task

        logging.info("Closing healthcheck server")
        self.healthcheck_server.close()
        await self.healthcheck_server.wait_closed()

        logging.info("Goodbye")
        await self.logout()

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
        # Any subscribed channels from this guild will be removed later by
        # send_notification.

    async def set_playing(self, title: str) -> None:
        await self.change_presence(activity=discord.Game(name=title))

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        message_parts = message.content.lower().split(" ")
        if message_parts[0] != config.BOT_COMMAND_PREFIX:
            return

        to_send = None

        try:
            command_used = message_parts[1]
            run_command = commands.COMMAND_LOOKUP[command_used]
            to_send = await run_command(
                client=self, message=message, operands=message_parts[2:]
            )

        except (KeyError, IndexError):
            pass  # Message contained wrong or no command
        except TypeError:
            logging.exception(f"run_command TypeError: {message.content=}")

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
            if isinstance(to_send, discord.Embed):
                if embeds.embed_size_ok(to_send):
                    await channel.send(embed=to_send)
                else:
                    logging.warning("Embed is too large to send")
            else:
                await channel.send(to_send)

        except discord.errors.Forbidden:
            # TODO: Count how many times this happens and unsub when n have happened?
            pass

        except discord.errors.HTTPException as ex:
            # Length/size is most likely cause,
            # see https://discord.com/developers/docs/resources/channel#embed-limits
            logging.warning(f"HTTPException: {ex}")

    async def send_notification(
        self,
        to_send: Union[str, discord.Embed],
        notification_type: NotificationType,
    ) -> None:
        """Send a notification message to all channels subscribed to the given type.

        Args:
            to_send: A string or discord.Embed object.
            notification_type: The type of notification being sent.

        """
        channel_ids = await self.ds.get_subbed_channels()
        invalid_ids = set()

        for channel_id in channel_ids:
            subscription_opts = channel_ids[channel_id]

            if (
                subscription_opts.notification_type != NotificationType.all
                and subscription_opts.notification_type != notification_type
            ):
                continue

            channel = self.get_channel(channel_id)
            if channel is None:
                invalid_ids.add(channel_id)
                continue

            await self._send_s(channel, to_send)

            if notification_type == NotificationType.launch:
                mentions = subscription_opts.launch_mentions
                if mentions != "":
                    await self._send_s(channel, mentions)

        for channel_id in invalid_ids:
            await self.ds.remove_subbed_channel(str(channel_id))
