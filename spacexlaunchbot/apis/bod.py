"""Handles interactions with the bots.ondiscord.xyz API
"""

import aiohttp
import logging

import config

BOD_URL = f"https://bots.ondiscord.xyz/bot-api/bots/{config.BOT_CLIENT_ID}/guildss"
BOD_HEADERS = {
    "Authorization": config.API_TOKEN_BOD,
    "Content-Type": "application/json",
}


async def update_guild_count(guild_count: int):
    logging.info(f"Sending a guild_count of {guild_count} to BOD")

    async with aiohttp.ClientSession() as session:
        await session.post(
            BOD_URL, json={"guildCount": guild_count}, headers=BOD_HEADERS
        )
