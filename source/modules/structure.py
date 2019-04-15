"""
General functions and variables used throughout the bot
"""

import sys
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from os import path
from datetime import datetime
import config

logger = logging.getLogger(__name__)


def fatalError(message):
    logger.critical(message)
    sys.exit(-1)


async def UTCFromTS(timestamp):
    """
    Get a UTC string from a unix timestamp
    """
    try:
        formattedDate = datetime.utcfromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return f"{formattedDate} UTC"
    except TypeError:
        # timestamp is not int
        return "To Be Announced"


def setupLogging():
    # Setup logging (direct logging to file, only log INFO level and above)
    logFileHandler = TimedRotatingFileHandler(
        filename=config.LOG_PATH, when="W0", backupCount=10, encoding="UTF-8"
    )
    logFileHandler.setFormatter(logging.Formatter(config.LOG_FORMAT))

    logging.basicConfig(level=logging.INFO, handlers=[logFileHandler])

    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)
