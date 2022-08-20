import asyncio
import logging
import platform
import signal
from typing import Union

import asyncpg
import discord
from discord import app_commands

from . import apis, commands, config, embeds, storage
from .notifications import NotificationType, check_and_send_notifications
from .utils import sys_info

ONE_MINUTE = 60


class SpaceXLaunchBotClient(discord.Client):
    # - The signals package is a bit iffy when it comes to pylint.
    #   See https://github.com/PyCQA/pylint/issues/2804
    # - Disable line-too-long because I'm lazy
    # pylint: disable=no-member,line-too-long,too-many-public-methods

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=discord.Intents.default())
        logging.info("Client initialised")
        logging.info(sys_info())
        self.tree = app_commands.CommandTree(self)
        self.tree_synced = False

    async def setup_hook(self):
        # pylint: disable=attribute-defined-outside-init

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

        logging.info("Creating a connection pool for DB")
        self.db_pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
        )
        logging.info(
            f"Pooled with {self.db_pool.get_size()}/{self.db_pool.get_max_size()} connections"
        )

        self.ds = storage.DataStore(
            self.db_pool,
            config.PICKLE_DUMP_LOCATION,
        )
        logging.info("Data storage initialised")

        self.notification_task = self.loop.create_task(self.start_notification_loop())
        self.counts_task = self.loop.create_task(self.start_db_counts_loop())
        # self.healthcheck_server = discordhealthcheck.start(self)

        self.dc_logger: Union[asyncio.Task, None] = None

    @property
    def latency_ms(self) -> int:
        """Converts the latency property to an int representing the value in ms."""
        return int(self.latency * 1000)

    #
    # on_ methods
    #

    async def on_connect(self) -> None:
        logging.info(f"Connected to Discord API with a latency of {self.latency_ms}ms")

    async def on_disconnect(self) -> None:
        # Wait 2 seconds, if we don't reconnect, log it.
        # pylint: disable=attribute-defined-outside-init
        self.dc_logger = self.loop.create_task(self.disconnected_logger())

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

        self.tree.command(
            name="nextlaunch",
            description="Send the latest launch schedule message to the current channel",
        )(self.command_next_launch)

        self.tree.command(
            name="launch",
            description="Send the launch schedule message for the given launch number to the current channel",
        )(self.command_launch)

        self.tree.command(
            name="add",
            description="Add the current channel to the notification service with the type; all, schedule, or launch",
        )(self.command_add)

        self.tree.command(
            name="remove",
            description="Remove the current channel from the notification service",
        )(self.command_remove)

        self.tree.command(
            name="info",
            description="Send information about the bot to the current channel",
        )(self.command_info)

        self.tree.command(name="help", description="List these commands")(
            self.command_help
        )

        # self.tree.command(name="debug_launch_embed", description="")(
        #     self.command_debug_launch_embed
        # )
        # self.tree.command(name="reset_notification_task_store", description="")(
        #     self.command_reset_notification_task_store
        # )
        # self.tree.command(name="shutdown", description="")(self.command_shutdown)

        if not self.tree_synced:
            logging.info("Syncing command tree")
            await self.tree.sync()
            self.tree_synced = True
            logging.info("Synced command tree")

        await self.set_playing(config.BOT_GAME_NAME)
        await self.update_website_metrics()

    async def on_guild_join(self, guild) -> None:
        logging.info(f"Joined guild, ID: {guild.id}")
        await self.update_website_metrics()
        await self.ds.register_metric("guild_join", str(guild.id))

    async def on_guild_remove(self, guild) -> None:
        logging.info(f"Removed from guild, ID: {guild.id}")
        await self.update_website_metrics()
        await self.ds.register_metric("guild_remove", str(guild.id))
        # Any subscribed channels from this guild will be removed later by
        # send_notification.

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        message_parts = message.content.lower().split(" ")
        to_send = None

        try:
            if message_parts[0] == config.BOT_MENTION_STR:
                command_used = "help"
            elif message_parts[0] != config.BOT_COMMAND_PREFIX:
                return
            else:
                command_used = message_parts[1]

            run_command = commands.COMMAND_LOOKUP[command_used]
            to_send = await run_command(
                client=self, message=message, operands=message_parts[2:]
            )
            await self.ds.register_metric(
                f"command_{command_used}", str(message.guild.id)
            )

        except (KeyError, IndexError):
            pass  # Message contained wrong or no command
        except TypeError:
            logging.exception(f"run_command TypeError: {message.content=}")

        if to_send is None:
            return

        await self._send_s(message.channel, to_send)

    #
    # Helpers
    #

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

    async def update_website_metrics(self) -> None:
        """Update bot list websites with guild count"""
        guild_count = len(self.guilds)
        logging.info(f"Updating bot lists with a guild_count of {guild_count}")
        await apis.bot_lists.post_all_bot_lists(guild_count)

    #
    # State change
    #

    async def shutdown(self, sig: Union[None, signal.Signals] = None) -> None:
        """Disconnects from Discord and cancels asyncio tasks"""
        logging.info("Shutdown called")

        if sig is not None:
            logging.info(f"Shutdown due to signal: {sig.name}")

        logging.info("Cancelling notification_task")
        self.notification_task.cancel()
        await self.notification_task

        logging.info("Cancelling counts_task")
        self.counts_task.cancel()
        await self.counts_task

        # logging.info("Closing healthcheck server")
        # self.healthcheck_server.close()
        # await self.healthcheck_server.wait_closed()

        logging.info("Goodbye")
        await self.close()

    async def set_playing(self, title: str) -> None:
        await self.change_presence(activity=discord.Game(name=title))

    #
    # Message sending
    #

    @staticmethod
    async def _send_s(
        channel,
        to_send: Union[str, discord.Embed],
    ) -> None:
        """Safely send a text / embed message to a channel. Logs any errors that occur.

        Args:
            channel: A discord.Channel object.
            to_send: A string or discord.Embed object.

        """
        try:
            if isinstance(to_send, embeds.BetterEmbed):
                if to_send.size_ok():
                    await channel.send(embed=to_send)
                else:
                    logging.warning("Embed is too large to send")
            elif isinstance(to_send, discord.Embed):
                await channel.send(embed=to_send)
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

            if subscription_opts.notification_type not in [
                NotificationType.all,
                notification_type,
            ]:
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

    #
    # Background tasks
    # TODO: Consolidate shared code into boilerplate method.
    #

    async def start_db_counts_loop(self) -> None:
        """A loop that every hour sends the guild and subscribed counts to the db."""
        logging.info("Waiting for client ready")
        await self.wait_until_ready()
        logging.info("Starting")

        while not self.is_closed():
            try:
                await self.ds.update_counts(len(self.guilds))
                await asyncio.sleep(ONE_MINUTE * 60)
            except asyncio.CancelledError:
                logging.info("Cancelled, stopping")
                break

        logging.info("Loop finished")

    async def start_notification_loop(self) -> None:
        """A loop that sends out launching soon & launch info notifications."""
        logging.info("Waiting for client ready")
        await self.wait_until_ready()
        logging.info("Starting")

        while not self.is_closed():
            try:
                await check_and_send_notifications(self)
                await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
            except asyncio.CancelledError:
                logging.info("Cancelled, stopping")
                break

        logging.info("Loop finished, saving data")
        self.ds.save_state()

    #
    # Slash command helpers
    #

    # @staticmethod
    # def interaction_from_owner(interaction: discord.Interaction):
    #     return interaction.user.id == config.BOT_OWNER_ID

    @staticmethod
    def interaction_from_admin(interaction: discord.Interaction):
        return interaction.user.resolved_permissions.administrator  # type: ignore

    #
    # Slash commands
    #

    async def command_next_launch(self, interaction: discord.Interaction):
        response: discord.Embed
        next_launch_dict = await apis.spacex.get_launch_dict()
        if next_launch_dict == {}:
            response = embeds.API_ERROR_EMBED
        else:
            response = embeds.create_schedule_embed(next_launch_dict)
        await interaction.response.send_message(embed=response)

    async def command_launch(
        self, interaction: discord.Interaction, launch_number: int
    ):
        response: discord.Embed
        launch_dict = await apis.spacex.get_launch_dict(launch_number)
        if launch_dict == {}:
            response = embeds.API_ERROR_EMBED
        else:
            response = embeds.create_schedule_embed(launch_dict)
        await interaction.response.send_message(embed=response)

    async def command_add(
        self,
        interaction: discord.Interaction,
        notification_type: str,
        notification_mentions: str,
    ):
        if self.interaction_from_admin(interaction) is False:
            await interaction.response.send_message(
                embed=embeds.ADMIN_PERMISSION_REQUIRED
            )
            return

        response: discord.Embed

        try:
            notification_type = NotificationType[notification_type]  # type: ignore
        except KeyError:
            await interaction.response.send_message(
                embed=embeds.create_interaction_embed(
                    'Invalid notification type, try "all", "schedule", or "launch"',
                    success=False,
                )
            )
            return

        notif_mentions_str = " ".join(notification_mentions)

        added = await self.ds.add_subbed_channel(
            str(interaction.channel_id),
            interaction.channel.name,  # type: ignore
            str(interaction.guild_id),
            notification_type,
            notif_mentions_str,
        )
        if added is False:
            response = embeds.create_interaction_embed(
                "This channel is already subscribed to the notification service",
                success=False,
            )
        else:
            logging.info(f"{interaction.channel_id} subscribed to {notification_type}")
            response = embeds.create_interaction_embed(
                "This channel has been added to the notification service"
            )
        await interaction.response.send_message(embed=response)

    async def command_remove(self, interaction: discord.Interaction):
        if self.interaction_from_admin(interaction) is False:
            await interaction.response.send_message(
                embed=embeds.ADMIN_PERMISSION_REQUIRED
            )
            return

        response: discord.Embed

        cid = str(interaction.channel_id)
        if await self.ds.remove_subbed_channel(cid) is False:
            response = embeds.create_interaction_embed(
                "This channel was not previously subscribed to the notification service",
                success=False,
            )
        else:
            logging.info(f"{interaction.channel_id} unsubscribed")
            response = embeds.create_interaction_embed(
                "This channel has been removed from the notification service"
            )
        await interaction.response.send_message(embed=response)

    async def command_info(self, interaction: discord.Interaction):
        guild_count = len(self.guilds)
        channel_count = await self.ds.subbed_channels_count()
        await interaction.response.send_message(
            embed=embeds.create_info_embed(guild_count, channel_count, self.latency_ms)
        )

    async def command_help(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=embeds.HELP_EMBED)

    # async def command_debug_launch_embed(
    #     self, interaction: discord.Interaction, launch_number: int
    # ):
    #     """Send a launch notification embed for the given launch."""
    #     if self.interaction_from_owner(interaction) == False:
    #         return

    #     response: discord.Embed

    #     launch_dict = await apis.spacex.get_launch_dict(launch_number)
    #     if launch_dict == {}:
    #         await interaction.response.send_message("API returned `{}`")
    #     else:
    #         await interaction.response.send_message(
    #             embed=embeds.create_launch_embed(launch_dict)
    #         )

    # async def command_reset_notification_task_store(
    #     self, interaction: discord.Interaction
    # ):
    #     """Reset notification_task_store to default (will trigger new notifications)."""
    #     if self.interaction_from_owner(interaction) == False:
    #         return
    #     logging.warning("reset notification task store command called")
    #     self.ds.set_notification_task_vars(False, {})
    #     await interaction.response.send_message(
    #         "Reset using `set_notification_task_vars(False, {})`"
    #     )

    # async def command_shutdown(self, interaction: discord.Interaction):
    #     if self.interaction_from_owner(interaction) == False:
    #         return
    #     logging.info("shutdown command called")
    #     await interaction.response.send_message("cya bitch")
    #     await self.shutdown()
