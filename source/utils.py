import sys

botInfo = """
**SpaceX-Launch-Bot**

This bot displays information about the latest upcoming SpaceX launches from the r/Space-X API

*API: https://github.com/r-spacex/SpaceX-API*
*Bot source: https://github.com/thatguywiththatname/SpaceX-Launch-Bot*
"""

helpText = """
Command prefix: {prefix}

Commands:
 • `!addchannel` - Subscribe the channel to the bots notification service - admins only
 • `!nextlaunch` - Show info about the next upcoming launch - any user can use this command
 • `!info` - Information about the bot - any user can use this command
 • `!help` - List these commands - any user can use this command
"""

def err(message):
    print("\nERROR:\n" + message)
    sys.exit(-1)
