import logging
from typing import Dict

import aiohttp

from .. import config


async def _post_count_to_bot_list(bl_data: Dict[str, str], guild_count: int) -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(
            bl_data["url"],
            json={bl_data["guild_count_parameter"]: guild_count},
            headers={
                "Authorization": bl_data["token"],
                "Content-Type": "application/json",
            },
        )


async def post_all_bot_lists(guild_count: int) -> None:
    if config.INDEV:
        logging.info("Skipping as we are in dev environment")
        return
    for data in config.BOT_LIST_DATA:
        await _post_count_to_bot_list(data, guild_count)
