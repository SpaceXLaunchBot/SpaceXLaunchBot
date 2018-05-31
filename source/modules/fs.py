"""
For dealing with file system interactions, such as loading and saving data
"""

from discord import Embed
from os import path
import logging
import asyncio
import pickle
import json

from modules.errors import fatalError, nextLaunchErrorEmbed

logger = logging.getLogger(__name__)

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
# Path has ../ as it is resolved from this files location
localDataPath = path.join(path.dirname(path.abspath(__file__)), "..", "resources", "data.pkl")
localDataLock = asyncio.Lock()

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

# Don't need to use lock right now as this happens during import
# Load data.pkl into variable, if not exists, use default and save it to file
localData = {"subscribedChannels": [], "latestLaunchInfoEmbedDict": nextLaunchErrorEmbed.to_dict(), "launchNotifSent": False}
try:
    with open(localDataPath, "rb") as f:
        localData = pickle.load(f)
except FileNotFoundError:
    # No .pkl, save default to file
    logger.warning("data.pkl not found, saving default localData")
    saveLocalDataSync()

"""
Load local config file and create a dictionary that can be accessed by everything
that imports this module
"""
configFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "config", "config.json")
# TODO: Check for needed keys
try:
    with open(configFilePath, "r") as inFile:
        config = json.load(inFile)
except FileNotFoundError:
    fatalError("Configuration file / directory not found")
