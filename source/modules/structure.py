"""
General functions and variables used throughout the bot
"""

import sys
import json
import logging
from os import path, environ
from datetime import datetime

logger = logging.getLogger(__name__)

def fatalError(message):
    logger.critical(message)
    sys.exit(-1)

def loadEnvVar(varName):
    """
    Returns the environment variable $varName, or exits program with error msg
    """
    try:
        return environ[varName]
    except KeyError:
        fatalError(f"Environment Variable \"{varName}\" cannot be found")

async def isInt(possiblyInteger):
    """
    An async function that returns True if the parameter is an integer
    """
    try:
        int(possiblyInteger)
        return True
    except ValueError:
        return False

async def launchTimeFromTS(timestamp):
    """
    Get a launch time string from a unix timestamp
    """
    if await isInt(timestamp):
        formattedDate = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return f"{formattedDate} UTC"
    return "To Be Announced"

# Load local config file into a dictionary that can be exported
configFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "config", "config.json")
# TODO: Update neededKeys
neededKeys = ["commandPrefix", "apiCheckInterval", "launchNotificationDelta", "logFormat"]
try:
    with open(configFilePath, "r") as inFile:
        config = json.load(inFile)
    for key in neededKeys:
        if key not in config:
            fatalError(f"Cannot find required key: {key} in configuration file")
except FileNotFoundError:
    fatalError("Configuration file / directory not found")
