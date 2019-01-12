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
    """
    Log message and exit with status code -1
    """
    logger.critical(message)
    sys.exit(-1)


def loadEnvVar(varName):
    """
    Returns the environment variable varName, or exits program with error msg
    """
    try:
        return environ[varName]
    except KeyError:
        fatalError(f'Environment Variable "{varName}" cannot be found')


async def convertToInt(possiblyInteger):
    """
    An async function that converts possiblyInteger to an integer and returns it
    If this fails then it returns False
    """
    try:
        return int(possiblyInteger)
    except ValueError:
        return False


async def launchTimeFromTS(timestamp):
    """
    Get a launch time string from a unix timestamp
    """
    try:
        formattedDate = datetime.utcfromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return f"{formattedDate} UTC"
    except TypeError:
        # timestamp is not int
        return "To Be Announced"


"""
Initialise globally used variables
"""

# Load local config file into a dictionary that can be exported
configFilePath = path.join(
    path.dirname(path.abspath(__file__)), "..", "config", "config.json"
)
neededKeys = [
    "ownerID",
    "commandPrefix",
    "apiCheckInterval",
    "launchSoonDelta",
    "logFilePath",
    "logFormat",
    "colours",
]
try:
    with open(configFilePath, "r") as inFile:
        config = json.load(inFile)
    for key in neededKeys:
        if key not in config:
            fatalError(f"Cannot find required key: {key} in configuration file")
except FileNotFoundError:
    fatalError("Configuration file / directory not found")

# Setup logging (direct logging to file, only log INFO level and above)
# Do this before other imports as some local modules use logging when imported
logFilePath = config["logFilePath"]
handler = logging.FileHandler(filename=logFilePath, encoding="UTF-8", mode="a")
handler.setFormatter(logging.Formatter(config["logFormat"]))
logging.basicConfig(level=logging.INFO, handlers=[handler])
# Change discord to only log ERROR level and above
logging.getLogger("discord").setLevel(logging.ERROR)
