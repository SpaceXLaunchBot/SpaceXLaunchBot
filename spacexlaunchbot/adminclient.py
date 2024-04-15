import logging

import discord

from . import config, embeds
from .apis import ll2
from .discordclient import SpaceXLaunchBotClient
from .notifications import NotificationType


class AdminSpaceXLaunchBotClient(SpaceXLaunchBotClient):
    """For local debugging ONLY"""

    async def on_ready(self) -> None:
        logging.warning("Adding admin commands to command tree")

        self.tree.command(
            name="reset_notification_task_store",
            description="Reset notification_task_store to default",
        )(self.command_reset_notification_task_store)

        self.tree.command(
            name="debug_launch_embed",
            description="Send a launch notification embed for the given launch",
        )(self.command_debug_launch_embed)

        self.tree.command(
            name="trigger_launch_notification",
            description="Trigger a standard launch notification",
        )(self.command_trigger_launch_notification)

        await super().on_ready()

    async def command_reset_notification_task_store(
        self, interaction: discord.Interaction
    ):
        """Reset notification_task_store to default (will trigger new notifications)."""
        if interaction.user.id != config.BOT_OWNER_ID:
            logging.warning("command called by non owner, doing nothing")
            return
        self.ds.set_notification_task_vars(False, {})
        await interaction.response.send_message(
            "Reset using `set_notification_task_vars(False, {})`"
        )

    async def command_debug_launch_embed(
        self, interaction: discord.Interaction, launch: int = 0
    ):
        """Send a launch notification embed for the given launch."""
        if interaction.user.id != config.BOT_OWNER_ID:
            logging.warning("command called by non owner, doing nothing")
            return
        next_launch_dict = await ll2.get_launch_dict(launch)
        launch_embed = embeds.create_launch_embed(next_launch_dict)
        await interaction.response.send_message(embed=launch_embed)

    async def command_trigger_launch_notification(
        self, interaction: discord.Interaction, launch: int = 0
    ):
        """Trigger a standard launch notification."""
        if interaction.user.id != config.BOT_OWNER_ID:
            logging.warning("command called by non owner, doing nothing")
            return
        next_launch_dict = await ll2.get_launch_dict(launch)
        launch_embed = embeds.create_launch_embed(next_launch_dict)
        await interaction.response.send_message("on it's way")
        await self.send_notification(launch_embed, NotificationType.launch)
