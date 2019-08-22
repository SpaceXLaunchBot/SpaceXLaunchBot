import logging
import logging.handlers
import datetime
from typing import Union

import config


async def utc_from_ts(timestamp: Union[int, None]) -> str:
    """Convert a unix timestamp to a formatted date string.

    Args:
        timestamp: A unix timestamp. Can be None.

    Returns:
        The timestamp formatted as a date, or "To Be Announced" if timestamp is None.

    """
    if timestamp is None:
        return "To Be Announced"

    return datetime.datetime.utcfromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


async def setup_logging() -> None:
    """Setup logging.

    These settings will apply to any logging.info, error, debug, etc. call from now on
    This uses logging.basicConfig to setup the logging usage, which means this function
    has to be called before anything else even imports logging, otherwise the
    configuration set by this will not be used.
    """
    log_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=config.LOG_PATH, when="W0", backupCount=10, encoding="UTF-8"
    )
    log_file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))

    logging.basicConfig(level=config.LOG_LEVEL, handlers=[log_file_handler])

    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)
