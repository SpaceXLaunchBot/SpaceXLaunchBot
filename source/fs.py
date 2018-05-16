"""
fs.py

For dealing with file system interactions, such as loading and saving data
"""

from discord import Embed
from os import path
import pickle
import json

from errors import fatalError, nextLaunchErrorEmbed

# Absolute paths are better
localDataPath = path.join(path.dirname(path.abspath(__file__)), "resources/data.pkl") 
configFilePath = path.join(path.dirname(path.abspath(__file__)), "config/config.json") 

async def saveLocalData(dictObj):
    with open(localDataPath, "wb") as f:
        pickle.dump(dictObj, f, pickle.HIGHEST_PROTOCOL)

def saveLocalDataSync(dictObj):
    """
    Because it isn't always called from inside an async loop
    """
    with open(localDataPath, "wb") as f:
        pickle.dump(dictObj, f, pickle.HIGHEST_PROTOCOL)

def loadLocalData():
    try:
        with open(localDataPath, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        # No .pkl, create default dict, save to file & return
        temp = {"subscribedChannels": [], "latestLaunchInfoEmbed": nextLaunchErrorEmbed, "launchNotifSent":False}
        saveLocalDataSync(temp)
        return temp

def loadConfig():
    # TODO: Check for needed keys
    try:
        with open(configFilePath, "r") as inFile:
            return json.load(inFile)
    except FileNotFoundError:
        fatalError("Configuration file / directory not found")
