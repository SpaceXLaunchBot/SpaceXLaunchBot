"""
Messages / embeds that won't be dynamically changing, such as the help message
"""

from discord import Embed

from modules.colours import hexColours
from modules import fs

infoEmbed = Embed(
    title="SpaceX-Launch-Bot Information",
    description="I am a bot for providing news and information about upcoming SpaceX launches\nI also provide a notification service for launch information and reminders for launches happening soon",
    color=hexColours["falconRed"]
)
infoEmbed.add_field(name="Website", value="http://spacex-launch-bot.gq")
infoEmbed.add_field(name="Github", value="https://github.com/r-spacex/SpaceX-Launch-Bot")
infoEmbed.add_field(name="Contact", value="If you have any questions or suggestions, you can message my owner, <@263412940869206027>, or raise an issue in the Github repo")

helpEmbed = Embed(
    title="SpaceX-Launch-Bot Commands",
    description=f"Command prefix: {fs.config['commandPrefix']}",
    color=hexColours["falconRed"]
)
helpEmbed.add_field(name="nextlaunch", value="Show info about the next upcoming launch\n*Any user can use this command*")
helpEmbed.add_field(name="addchannel", value="Add the current channel to the bots launch notification service\n*Only admins can use this command*")
helpEmbed.add_field(name="removechannel", value="Remove the current channel to the bots launch notification service\n*Only admins can use this command*")
helpEmbed.add_field(name="info", value="Information about this bot\n*Any user can use this command*")
helpEmbed.add_field(name="help", value="List these commands\n*Any user can use this command*")
