from discord import Embed, Colour

import config

# Use Github as image hosting
logo_base_url = (
    "https://raw.githubusercontent.com/r-spacex/SpaceX-Launch-Bot/master/images/logos"
)
rocket_id_images = {
    "falcon9": f"{logo_base_url}/falcon9.png",
    "falconheavy": f"{logo_base_url}/falconHeavy.png",
    "falcon1": f"{logo_base_url}/logo.jpg",
}

# Convert chosen RGB values into usable Colour objects
error_red = Colour.from_rgb(*config.EMBED_COLOURS["error_red"])
falcon_red = Colour.from_rgb(*config.EMBED_COLOURS["falcon_red"])

owner_mention = f"<@{config.OWNER_ID}>"

help_embed = Embed(
    title="SpaceX-Launch-Bot Commands",
    description=f"Command prefix: {config.COMMAND_PREFIX}",
    color=falcon_red,
)
help_embed.add_field(
    name="nextlaunch",
    value="Show info about the next upcoming launch\n*Any user can use this command*",
)
help_embed.add_field(
    name="addchannel",
    value="Add the current channel to the bots notification service\n*Only admins can use this command*",
)
help_embed.add_field(
    name="removechannel",
    value="Remove the current channel to the bots notification service\n*Only admins can use this command*",
)
help_embed.add_field(
    name="setmentions @mention",
    value="Set roles/users to be mentioned when a 'launching soon' message is sent. Can be formatted with multiple mentions in any order, like this: `!addping @role1 @user1 @role2`. Calling `!addping` multiple times will not stack the mentions, it will just overwrite your previous mentions\n*Only admins can use this command*",
)
help_embed.add_field(
    name="removementions",
    value="Remove all mentions set for the current guild\n*Only admins can use this command*",
)
help_embed.add_field(
    name="getmentions",
    value="Get mentions set for the current guild\n*Only admins can use this command*",
)
help_embed.add_field(
    name="info", value="Information about this bot\n*Any user can use this command*"
)
help_embed.add_field(
    name="help", value="List these commands\n*Any user can use this command*"
)

next_launch_error_embed = Embed(
    title="Error",
    description=f"An launch_info_embed error occurred, contact {owner_mention}",
    color=error_red,
)
api_error_embed = Embed(
    title="Error",
    description=f"An API error occurred, contact {owner_mention}",
    color=error_red,
)
general_error_embed = Embed(
    title="Error",
    description=f"An error occurred, contact {owner_mention}",
    color=error_red,
)
db_error_embed = Embed(
    title="Error",
    description=f"A database error occurred, contact {owner_mention}",
    color=error_red,
)
