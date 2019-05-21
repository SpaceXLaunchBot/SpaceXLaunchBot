import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

import config


async def utc_from_ts(timestamp):
    """Get a UTC string from a unix timestamp
    If timestamp is not an int, returns "To Be Announced"
    """
    try:
        formatted_date = datetime.utcfromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return f"{formatted_date} UTC"
    except TypeError:
        # timestamp is not int
        return "To Be Announced"


def setup_logging():
    """Setup logging (direct logging to file, only log INFO level and above)
    """
    log_file_handler = TimedRotatingFileHandler(
        filename=config.LOG_PATH, when="W0", backupCount=10, encoding="UTF-8"
    )
    log_file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))

    logging.basicConfig(level=logging.INFO, handlers=[log_file_handler])

    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)
