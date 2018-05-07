from discord import Embed, errors
import pickle
import sys
import os

nextLaunchErrorEmbed = Embed(title="Error", description="nextLaunchEmbed error, contact @Dragon#0571", color=0xFF0000)

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

async def safeTextMessage(client, channel, message):
    """
    Send a text message to a client, and if an error occurs,
    safely supress it
    """
    try:
        return await client.send_message(channel, message)
    except errors.HTTPException:
        return  # API down, Message too big, etc.
    except errors.Forbidden:
        return  # No permission to message this channel

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
        temp = {"subscribedChannels": [], "nextLaunchEmbed": nextLaunchErrorEmbed}
        saveDict(temp)
        return temp

async def isInt(possiblyInteger):
    try:
        int(possiblyInteger)
        return True
    except ValueError:
        return False
