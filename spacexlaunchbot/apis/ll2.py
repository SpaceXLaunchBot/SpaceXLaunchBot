"""Handles interactions with the Launch Library 2 API.

As of 22/11/22, API rate limit is 15 req/hour per IP.
"""

import logging
from typing import Dict

from aiohttp import ClientConnectorError, ClientError, ContentTypeError
from aiohttp_client_cache import CachedSession, SQLiteBackend

from .. import config

# Use ratelimit-free but innacurate API if developing (avoids rate limiting).
_SUBDOMAIN = "lldev" if config.INDEV else "ll"

_DOMAIN = (
    f"https://{_SUBDOMAIN}.thespacedevs.com/2.2.0/launch/upcoming?limit=1&lsp__id=121"
)

# Cache all requests to launch library.
# Will help with a potential fix for the /launch command.
# We use NOTIF_TASK_INTERVAL as we set that to lowest possible for rate limit.
_REQUEST_CACHE = SQLiteBackend(
    cache_name="./ll2.cache.sqlite", expire_after=60 * config.NOTIF_TASK_INTERVAL
)


async def get_launch_dict(launch_number: int = 0) -> Dict:
    """Get a launch information dictionary for the given launch.

    If launch_number <= 0 (the default), get the next upcoming launch.

    """
    # pylint: disable=too-many-return-statements

    ll2_api_url = _DOMAIN

    # TODO: /launch command fix
    if launch_number > 0:
        # ll2_api_url = ?
        return {}

    try:
        async with CachedSession(cache=_REQUEST_CACHE) as session:
            async with session.get(ll2_api_url, allow_redirects=True) as response:
                if response.status != 200:
                    logging.error(f"Failed with response status: {response.status}")
                    return {}

                json = await response.json()
                results = json.get("results", [])

                if len(results) == 0:
                    logging.error("Request returned no results")
                    return {}

                return results[0]

    except ClientConnectorError:
        logging.error("Cannot connect to thespacedevs.com")
        return {}

    except ContentTypeError:
        logging.error("JSON decode failed")
        return {}

    except ClientError:
        logging.error("Caught aiohttp.ClientError", exc_info=True)
        return {}
