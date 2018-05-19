"""
For dealing with file system interactions, such as loading and saving data
"""

from discord import Embed
from os import path
import asyncio
import pickle
import json

from errors import fatalError, nextLaunchErrorEmbed

"""
+ Load localData from file into variable, which stays in this module but can be edited
    by anything that imports this module
+ localData is a dictionary that has a lock (as it is accessed a lot in multiple
    functions) and is used to store multiple things:
        - A list of channel IDs that are subscribed
        - The latest launch information embed that was sent
        - Whether or not an active launch notification has been sent for the current launch
+ This is saved to and loaded from a file (so it persists through reboots/updates)
"""
localDataPath = path.join(path.dirname(path.abspath(__file__)), "resources/data.pkl")
localDataLock = asyncio.Lock()
# Don't need to use lock right now as this happens during import
localData = {"subscribedChannels": [], "latestLaunchInfoEmbed": nextLaunchErrorEmbed, "launchNotifSent": False}
try:
    with open(localDataPath, "rb") as f:
        localData = pickle.load(f)
except FileNotFoundError:
    # No .pkl, save default to file
    saveLocalDataSync(localData)

async def saveLocalData():
    """
    Saves this modules localData variable to the localDataPath
    """
    with open(localDataPath, "wb") as f:
        pickle.dump(localData, f, pickle.HIGHEST_PROTOCOL)

def saveLocalDataSync():
    """
    Because it isn't always called from inside an async loop
    """
    with open(localDataPath, "wb") as f:
        pickle.dump(localData, f, pickle.HIGHEST_PROTOCOL)


"""
Load local config file and create a dictionary that can be accessed by everything
that imports this module
"""
configFilePath = path.join(path.dirname(path.abspath(__file__)), "config/config.json")
# TODO: Check for needed keys
try:
    with open(configFilePath, "r") as inFile:
        config = json.load(inFile)
except FileNotFoundError:
    fatalError("Configuration file / directory not found")
