import datetime
import json
import logging
import platform
import sys
from typing import Union

import pytz
from discord import version_info

from .. import config, version


def utc_from_time(date_string: Union[str, None]) -> str:
    """Convert UTC time string to formatted string (legacy, kept for compatibility)."""
    if date_string is None:
        return "To Be Announced"
    return datetime.datetime.fromisoformat(date_string).strftime("%Y-%m-%d %H:%M:%S")


def convert_time_to_timezone(date_string: Union[str, None], timezone_str: str = "UTC") -> str:
    """Convert a UTC datetime string to a specified timezone.

    Args:
        date_string: ISO format datetime string in UTC.
        timezone_str: Target timezone name (e.g., 'America/New_York').

    Returns:
        Formatted datetime string in the target timezone.
    """
    if date_string is None:
        return "To Be Announced"
    
    try:
        # Parse the UTC datetime
        utc_dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        
        # Convert to target timezone
        if timezone_str and timezone_str != "UTC":
            target_tz = pytz.timezone(timezone_str)
            local_dt = utc_dt.astimezone(target_tz)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, pytz.exceptions.UnknownTimeZoneError):
        # Fallback to UTC if timezone is invalid
        utc_dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC")


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
