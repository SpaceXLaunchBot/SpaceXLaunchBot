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

    # mypy complains unless we tell it that the values are dicts.
    body: Dict[str, Dict] = {
        "query": {},
        "options": {
            "limit": 1,
            "sort": {"flight_number": "asc"},
            "populate": [
                "payloads",
                "rocket",
                "launchpad",
                {
                    "path": "cores",
                    "populate": [
                        {"path": "landpad", "select": "name"},
                        {"path": "core", "select": "serial"},
                    ],
                },
            ],
        },
    }

    if launch_number <= 0:
        body["query"]["upcoming"] = True
    else:
        body["query"]["flight_number"] = launch_number

    spacex_api_url = "https://api.spacexdata.com/v4/launches/query"

    try:
        async with aiohttp.ClientSession() as session:
            # NOTE: For some reason, api.spacexdata.com seems to spam 308 redirects
            #  sometimes which for some reason causes this task to hang and maybe
            #  crash? Hopefully disallowing redirects will fix this.
            async with session.post(
                spacex_api_url, json=body, allow_redirects=False
            ) as response:
                if response.status != 200:
                    logging.error(f"Failed with response status: {response.status}")
                    return {}
                # Query endpoints return Mongo query responses.
                # Limit is set to 1 and it's pretty much guaranteed there will be data.
                return (await response.json())["docs"][0]

    except aiohttp.ClientConnectorError:
        logging.error("Cannot connect to api.spacexdata.com")
        return {}

    except aiohttp.ContentTypeError:
        logging.error("JSON decode failed")
        return {}

    except aiohttp.ClientError:
        logging.error("Caught aiohttp.ClientError", exc_info=True)
        return {}
