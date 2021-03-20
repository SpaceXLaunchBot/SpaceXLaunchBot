import asyncio
import datetime
import logging
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


async def disconnected_logger() -> None:
    """Sleep for 2 seconds then log a disconnect."""
    # NOTE: The whole reason for this function is so that the reconnect method can
    # cancel this function running as a task, this prevents the log filling up with
    # reconnection logs.
    try:
        await asyncio.sleep(2)
        logging.info("Disconnected from Discord API")
    except asyncio.CancelledError:
        pass
