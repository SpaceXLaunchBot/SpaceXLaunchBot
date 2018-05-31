"""
Setup logging realted stuff
"""

import logging
from os import path

from modules.fs import config

def setup():
    logFormat = config["logFormat"]

    # Do this before other imports as some local modules use logging when imported
    # Direct logging to file, only log INFO level and above
    logFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "..", "bot.log")
    handler = logging.FileHandler(filename=logFilePath, encoding="UTF-8", mode="a")
    handler.setFormatter(logging.Formatter(logFormat))
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    # Change discord to only log WARNING level and above
    logging.getLogger("discord").setLevel(logging.WARNING)
