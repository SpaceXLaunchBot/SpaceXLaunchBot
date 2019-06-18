"""Handles interactions with the discordbots.org API
"""

import aiohttp
import logging

import config


async def update_guild_count(guild_count):
    logging.info(f"Sending a guild_count of {guild_count} to DBL")
    async with aiohttp.ClientSession() as session:
        await session.post(
            config.DBL_URL,
            json={"server_count": guild_count},
            headers=config.DBL_HEADERS,
        )
