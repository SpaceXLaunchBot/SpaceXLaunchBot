from datetime import datetime
from discord import Embed
from os import path
import pickle
import sys

# Saved to the dictionary file by default
nextLaunchErrorEmbed = Embed(title="Error", description="launchInfoEmbed error, contact @Dragon#0571", color=0xFF0000)

botInfo = """
This bot displays information about the latest upcoming SpaceX launches from the r/Space-X API

*Website: https://r-spacex.github.io/SpaceX-Launch-Bot/*
*Github: https://github.com/r-spacex/SpaceX-Launch-Bot*
"""

helpText = """
Command prefix: {prefix}

Commands:
 • `nextlaunch` - Show info about the next upcoming launch - any user can use this command
 • `addchannel` - Add the current channel to the bots launch notification service - only admins can use this command
 • `removechannel` - Remove the current channel to the bots launch notification service - only admins can use this command
 • `info` - Information about the bot - any user can use this command
 • `help` - List these commands - any user can use this command
"""

# Absolute paths are better
resourceFilePath = path.join(path.dirname(path.abspath(__file__)), "resources/data.pkl") 

def err(message):
    print("\nERROR:\n" + message)
    sys.exit(-1)

async def saveDict(dictObj):
    with open(resourceFilePath, "wb") as f:
        pickle.dump(dictObj, f, pickle.HIGHEST_PROTOCOL)

def saveDictSync(dictObj):
    """
    Because it isn't always called from inside an async loop
    """
    with open(resourceFilePath, "wb") as f:
        pickle.dump(dictObj, f, pickle.HIGHEST_PROTOCOL)

def loadDict():
    try:
        with open(resourceFilePath, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        # No .pkl, create default dict, save to file & return
        temp = {"subscribedChannels": [], "latestLaunchInfoEmbed": nextLaunchErrorEmbed, "launchNotifSent":False}
        saveDictSync(temp)
        return temp

async def isInt(possiblyInteger):
    try:
        int(possiblyInteger)
        return True
    except ValueError:
        return False

async def getUTCFromTimestamp(timestamp):
    dateIsInt = await isInt(timestamp)
    if dateIsInt:
        formattedDate = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return "{} UTC".format(formattedDate)
    return "To Be Announced"
