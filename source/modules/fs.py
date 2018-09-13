"""
For dealing with file system interactions, currently just config file(s)
"""

from modules.errors import fatalError
from os import path
import json

"""
Load local config file and create a dictionary that can be accessed by everything
that imports this module
"""
configFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "config", "config.json")
neededKeys =["commandPrefix", "apiCheckInterval", "launchNotificationDelta", "reaperInterval", "logFormat"]

try:
    with open(configFilePath, "r") as inFile:
        config = json.load(inFile)
    
    for key in neededKeys:
        if key not in config:
            fatalError(f"Cannot find required key: {key} in configuration file")

except FileNotFoundError:
    fatalError("Configuration file / directory not found")
