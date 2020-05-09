"""Handles interactions with the SpaceX API.

As of 13/01/19, API rate limit is 50 req/sec per IP.
"""

import logging
from typing import Dict

import aiohttp


async def get_launch_dict(launch_number: int = 0) -> Dict:
    """Get a launch information dictionary for the given launch.

    If launch_number <= 0 (the default), get the "next" launch.
    """

    route = launch_number if launch_number > 0 else "next"
    spacex_api_url = f"https://api.spacexdata.com/v3/launches/{route}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(spacex_api_url) as response:
                if response.status != 200:
                    logging.error(f"Response status: {response.status}")
                    return {}
                return await response.json()

    except aiohttp.client_exceptions.ClientConnectorError:
        logging.error("Cannot connect to api.spacexdata.com")
        return {}

    except aiohttp.ContentTypeError:
        logging.error("JSON decode failed")
        return {}
