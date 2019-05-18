"""Handles interactions with the SpaceX API
As of 13/01/19, API ratelimit is 50 req/sec per IP
"""

import aiohttp, logging

log = logging.getLogger(__name__)


async def get_next_launch_dict(previous=False):
    """Using aiohttp, get the latest launch info
    If previous=True, use data from previous launch (for debugging)
    Returns -1 on failure
    """

    if previous:
        route = "latest"
    else:
        route = "next"

    upcoming_launches_url = f"https://api.spacexdata.com/v3/launches/{route}"

    async with aiohttp.ClientSession() as session:
        async with session.get(upcoming_launches_url) as response:
            if response.status == 200:
                try:
                    next_launch_dict = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    # TODO: Test if this makes sense in actual log file
                    log.error("JSON decode failed")
                    return -1
            else:
                log.error(f"Response status: {response.status}")
                return -1
            return next_launch_dict
