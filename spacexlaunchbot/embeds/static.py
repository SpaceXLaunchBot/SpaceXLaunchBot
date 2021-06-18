from . import colours
from .better_embed import BetterEmbed
from .. import config

# pylint: disable=line-too-long

HELP_EMBED = BetterEmbed(
    title="SpaceXLaunchBot Commands",
    description=f"Command prefix: `{config.BOT_COMMAND_PREFIX}`",
    color=colours.RED_FALCON,
    inline_fields=False,
    fields=[
        [
            "nextlaunch",
            "Send the latest launch schedule message to the current channel",
        ],
        [
            "launch [launch number]",
            "Send the launch schedule message for the given launch number to the current channel",
        ],
        [
            "add [type] #channel, @user, @role, etc.",
            "Add the current channel to the notification service with the given notification type (`all`, `schedule`, or `launch`). If you chose `all` or `launch`, the second part can be a list of roles / channels / users to ping when a launch notification is sent\n*Only admins can use this command*",
        ],
        [
            "remove",
            "Remove the current channel from the notification service\n*Only admins can use this command*",
        ],
        ["info", "Send information about the bot to the current channel"],
        ["help", "List these commands"],
    ],
)

API_ERROR_EMBED = BetterEmbed(
    title="Error",
    description=f"An API error occurred, contact {config.BOT_OWNER_NAME}",
    color=colours.RED_ERROR,
)
