"""
Setup logging realted stuff
"""

import logging

from modules.fs import config

def setup():
    # Do this before other imports as some local modules use logging when imported
    # Direct logging to file, only log INFO level and above
    logFilePath = "/var/log/SLB/bot.log"
    handler = logging.FileHandler(filename=logFilePath, encoding="UTF-8", mode="a")
    handler.setFormatter(logging.Formatter(config["logFormat"]))
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)
