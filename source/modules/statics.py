"""
Messages / embeds / variables that won't be dynamically changing, such as the
colour objects, help message, and the various error messages. These are then
imported into other files
"""

from discord import Embed, Colour

from modules.structure import config

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
errorRed = Colour.from_rgb(*config["colours"]["errorRed"])
falconRed = Colour.from_rgb(*config["colours"]["falconRed"])

ownerMention = f"<@{config['ownerID']}>"

infoEmbed = Embed(
    title="SpaceX-Launch-Bot Information",
    description="I am a Discord bot for getting news and information about upcoming SpaceX launches ",
    color=falconRed,
)
infoEmbed.add_field(
    name="Github", value="https://github.com/r-spacex/SpaceX-Launch-Bot"
)
infoEmbed.add_field(
    name="Contact",
    value=f"If you have any questions or suggestions, you can message my owner, {ownerMention}, or raise an issue in the Github repo",
)

helpEmbed = Embed(
    title="SpaceX-Launch-Bot Commands",
    description=f"Command prefix: {config['commandPrefix']}",
    color=falconRed,
)
helpEmbed.add_field(
    name="nextlaunch",
    value="Show info about the next upcoming launch\n*Any user can use this command*",
)
helpEmbed.add_field(
    name="addchannel",
    value="Add the current channel to the bots launch notification service\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="removechannel",
    value="Remove the current channel to the bots launch notification service\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="addping @mention",
    value="Add roles/users to be pinged when the 'launching soon' (launch notification) message is sent. Can be formatted with multiple mentions in any order, like this: `!addping @role1 @user1 @role2`. Calling `!addping` multiple times will not stack the roles, it will just overwrite your previous settings\n*Only admins can use this command*",
)
helpEmbed.add_field(
    name="removeping",
    value="Stop any roles/users on the server being pinged when the 'launching soon' (launch notification) message is sent\n*Only admins can use this command*",
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
