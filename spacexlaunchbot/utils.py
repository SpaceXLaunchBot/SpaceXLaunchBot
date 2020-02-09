import datetime
import logging
import logging.handlers
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


def setup_logging() -> None:
    """Setup logging."""
    logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)

    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)
