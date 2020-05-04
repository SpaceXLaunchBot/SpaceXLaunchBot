from discord import Embed

import config

# Use Github as image hosting
LOGO_BASE_URL = (
    "https://raw.githubusercontent.com/r-spacex/SpaceXLaunchBot/master/images/logos"
)
ROCKET_ID_IMAGES = {
    "falcon9": f"{LOGO_BASE_URL}/falcon_9.png",
    "falconheavy": f"{LOGO_BASE_URL}/falcon_heavy.png",
    "falcon1": f"{LOGO_BASE_URL}/logo.jpg",
}

HELP_EMBED = Embed(
    title="SpaceXLaunchBot Commands",
    description=f"Command prefix: {config.BOT_COMMAND_PREFIX}",
    color=config.Colours.FALCON_RED,
)
HELP_EMBED.add_field(
    name="nextlaunch",
    value="Send the latest launch information message to the current channel",
)
HELP_EMBED.add_field(
    name="addchannel",
    value="Add the current channel to the notification service\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="removechannel",
    value="Remove the current channel from the notification service\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="setmentions @mention",
    value='Set roles/users to be mentioned when a "launching soon" message is sent. '
    "Can be formatted with multiple mentions in any order, like this: `slb setmentions"
    " @role1 @user1 @here`. Calling `setmentions` multiple times will not stack the "
    "mentions, it will just overwrite your previous mentions\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="removementions",
    value="Remove all mentions set for the current guild\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="getmentions",
    value='Show the mentions you have set for "launching soon" notifications\n'
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="info", value="Send information about the bot to the current channel"
)
HELP_EMBED.add_field(name="help", value="List these commands")

NEXT_LAUNCH_ERROR_EMBED = Embed(
    title="Error",
    description=f"An launch_info_embed error occurred, contact {config.BOT_OWNER}",
    color=config.COLOUR_ERROR_RED,
)
API_ERROR_EMBED = Embed(
    title="Error",
    description=f"An API error occurred, contact {config.BOT_OWNER}",
    color=config.COLOUR_ERROR_RED,
)
GENERAL_ERROR_EMBED = Embed(
    title="Error",
    description=f"An error occurred, contact {config.BOT_OWNER}",
    color=config.COLOUR_ERROR_RED,
)
DB_ERROR_EMBED = Embed(
    title="Error",
    description=f"A database error occurred, contact {config.BOT_OWNER}",
    color=config.COLOUR_ERROR_RED,
)

LEGACY_PREFIX_WARNING_EMBED = Embed(
    title="New Prefix In Use",
    description="You used a command with the old prefix (!), SpaceXLaunchBot has "
    'moved to using "slb" as a prefix, e.g. `slb help`. This warning will be removed '
    "soon.",
    color=config.COLOUR_INFO_ORANGE,
)
