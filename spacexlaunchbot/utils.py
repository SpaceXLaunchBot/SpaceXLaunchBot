import datetime
import json
import logging
import platform
import sys
from typing import Union

from . import config


def utc_from_ts(timestamp: Union[int, None]) -> str:
    """Convert a unix timestamp to a formatted date string.

    Args:
        timestamp: A unix timestamp. Can be None.

    Returns:
        The timestamp formatted as a date, or "To Be Announced" if timestamp is None.

    """
    if timestamp is None:
        return "To Be Announced"
    return datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def setup_logging() -> None:
    """Setup logging."""
    logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)


def md_link(name: str, url: str) -> str:
    """Makes strings easier to read when defining markdown links."""
    return f"[{name}]({url})"


def sys_info():
    """Returns a JSON string of system information (useful for debugging)."""
    return json.dumps(
        {
            "interpreter": sys.version,
            "platform": platform.system(),
            "platform-release": platform.release(),
            "platform-version": platform.version(),
            "architecture": platform.machine(),
        }
    )
