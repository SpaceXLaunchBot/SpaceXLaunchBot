from launchAPI import hexColours
from discord import Embed
import pickle
import sys
import os

newLaunchErrorEmbed = Embed(title="Error", description="nextLaunchEmbed error, contact @Dragon#0571", color=hexColours["errorRed"])

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

pickleProtocol = pickle.HIGHEST_PROTOCOL

# Absolute path
resourceFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/dict.pkl") 

def err(message):
    print("\nERROR:\n" + message)
    sys.exit(-1)

def saveDict(dictObj):
    with open(resourceFilePath, "wb") as f:
        pickle.dump(dictObj, f, pickleProtocol)

def loadDict():
    try:
        with open(resourceFilePath, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        # No .pkl, create default dict, save to file & return
        temp = {"subscribedChannels": [], "nextLaunchEmbed": newLaunchErrorEmbed}
        saveDict(temp)
        return temp
