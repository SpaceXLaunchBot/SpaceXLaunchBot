from discord import Embed, Colour

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

# Convert chosen RGB values into usable Colour objects
ERROR_RED = Colour.from_rgb(*config.EMBED_COLOURS["error_red"])
FALCON_RED = Colour.from_rgb(*config.EMBED_COLOURS["falcon_red"])

HELP_EMBED = Embed(
    title="SpaceXLaunchBot Commands",
    description=f"Command prefix: {config.BOT_COMMAND_PREFIX}",
    color=FALCON_RED,
)
HELP_EMBED.add_field(
    name="nextlaunch",
    value="Send the latest launch information message to the current channel\n"
    "*Any user can use this command*",
)
HELP_EMBED.add_field(
    name="addchannel",
    value="Add the current channel to the notification service\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="removechannel",
    value="Remove the current channel from the notification service"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="setmentions @mention",
    value="Set roles/users to be mentioned when a 'launching soon' message is sent. "
    "Can be formatted with multiple mentions in any order, like this: "
    "`!addping @role1 @user1 @role2`. Calling `setmentions` multiple times will not "
    "stack the mentions, it will just overwrite your previous mentions\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="removementions",
    value="Remove all mentions set for the current guild\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="getmentions",
    value="Send the mentions set for the current guild to the current channel\n"
    "*Only admins can use this command*",
)
HELP_EMBED.add_field(
    name="info",
    value="Send information about the bot to the current channel\n"
    "*Any user can use this command*",
)
HELP_EMBED.add_field(
    name="help", value="List these commands\n*Any user can use this command*"
)

NEXT_LAUNCH_ERROR_EMBED = Embed(
    title="Error",
    description=f"An launch_info_embed error occurred, contact {config.BOT_OWNER}",
    color=ERROR_RED,
)
API_ERROR_EMBED = Embed(
    title="Error",
    description=f"An API error occurred, contact {config.BOT_OWNER}",
    color=ERROR_RED,
)
GENERAL_ERROR_EMBED = Embed(
    title="Error",
    description=f"An error occurred, contact {config.BOT_OWNER}",
    color=ERROR_RED,
)
DB_ERROR_EMBED = Embed(
    title="Error",
    description=f"A database error occurred, contact {config.BOT_OWNER}",
    color=ERROR_RED,
)
