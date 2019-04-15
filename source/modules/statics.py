from discord import Embed, Colour

import config

# Use Github as image hosting
logoBaseURL = (
    "https://raw.githubusercontent.com/r-spacex/SpaceX-Launch-Bot/master/images/logos"
)
rocketIDImages = {
    "falcon9": f"{logoBaseURL}/falcon9.png",
    "falconheavy": f"{logoBaseURL}/falconHeavy.png",
    "falcon1": f"{logoBaseURL}/logo.jpg",
}

# Convert chosen RGB values into usable Colour objects
errorRed = Colour.from_rgb(*config.EMBED_COLOURS["errorRed"])
falconRed = Colour.from_rgb(*config.EMBED_COLOURS["falconRed"])

ownerMention = f"<@{config.OWNER_ID}>"

helpEmbed = Embed(
    title="SpaceX-Launch-Bot Commands",
    description=f"Command prefix: {config.COMMAND_PREFIX}",
    color=falconRed,
)
helpEmbed.add_field(
    name="nextlaunch",
    value="Show info about the next upcoming launch\n*Any user can use this command*",
)
helpEmbed.add_field(
    name="addchannel",
    value="Add the current channel to the bots notification service\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="removechannel",
    value="Remove the current channel to the bots notification service\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="setmentions @mention",
    value="Set roles/users to be mentioned when a 'launching soon' message is sent. Can be formatted with multiple mentions in any order, like this: `!addping @role1 @user1 @role2`. Calling `!addping` multiple times will not stack the mentions, it will just overwrite your previous mentions\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="removementions",
    value="Remove all mentions set for the current guild\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="getmentions",
    value="Get mentions set for the current guild\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="info", value="Information about this bot\n*Any user can use this command*"
)
helpEmbed.add_field(
    name="help", value="List these commands\n*Any user can use this command*"
)

nextLaunchErrorEmbed = Embed(
    title="Error",
    description=f"An launchInfoEmbed error occurred, contact {ownerMention}",
    color=errorRed,
)
apiErrorEmbed = Embed(
    title="Error",
    description=f"An API error occurred, contact {ownerMention}",
    color=errorRed,
)
generalErrorEmbed = Embed(
    title="Error",
    description=f"An error occurred, contact {ownerMention}",
    color=errorRed,
)
dbErrorEmbed = Embed(
    title="Error",
    description=f"A database error occurred, contact {ownerMention}",
    color=errorRed,
)
