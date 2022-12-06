from .. import config
from . import colours
from .better_embed import BetterEmbed

# pylint: disable=line-too-long

HELP_EMBED = BetterEmbed(
    title="SpaceXLaunchBot Commands",
    description="SpaceXLaunchbot now supports [slash commands](https://support.discord.com/hc/en-us/articles/1500000368501-Slash-Commands-FAQ)!\nSupport for message commands will end September 1st",
    color=colours.RED_FALCON,
    inline_fields=False,
    fields=[
        [
            "nextlaunch",
            "Send the latest launch schedule message to the current channel",
        ],
        [
            "launch [launch number]",
            "Currently disabled due to new API rate limits",
            # "Send the launch schedule message for the gi,ven launch number to the current channel",
        ],
        [
            "add [type] [mentions]",
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
    description=f"An API error occurred, please contact {config.BOT_OWNER_NAME}",
    color=colours.RED_ERROR,
)

ADMIN_PERMISSION_REQUIRED = BetterEmbed(
    title="Administrator Permission Required",
    description="",
    color=colours.RED_ERROR,
)
