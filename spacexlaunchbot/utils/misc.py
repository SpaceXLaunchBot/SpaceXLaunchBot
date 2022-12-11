import datetime
import json
import logging
import platform
import sys
from typing import Union

from discord import version_info

from .. import config, version


def utc_from_time(date_string: Union[str, None]) -> str:
    if date_string is None:
        return "To Be Announced"
    return datetime.datetime.fromisoformat(date_string).strftime("%Y-%m-%d %H:%M:%S")


def setup_logging() -> None:
    """Setup logging."""
    logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)


def md_link(name: str, url: str) -> str:
    """Makes strings easier to read when defining markdown links."""
    return f"[{name}]({url})"


def sys_info() -> str:
    """Returns a JSON string of system information (useful for debugging)."""
    return json.dumps(
        {
            "interpreter": sys.version,
            "platform": platform.system(),
            "platform-release": platform.release(),
            "platform-version": platform.version(),
            "architecture": platform.machine(),
            "discord-version_info": version_info,
            "indev": config.INDEV,
            "inside_docker": config.INSIDE_DOCKER,
            "commit-hash": version.HASH,
        }
    )
