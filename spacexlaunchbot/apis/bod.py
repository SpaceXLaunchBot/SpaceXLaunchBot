"""Handles interactions with the bots.ondiscord.xyz API.
"""

import logging

import aiohttp

import config

BOD_URL = f"https://bots.ondiscord.xyz/bot-api/bots/{config.BOT_CLIENT_ID}/guilds"
BOD_HEADERS = {
    "Authorization": config.API_TOKEN_BOD,
    "Content-Type": "application/json",
}


async def update_guild_count(guild_count: int) -> None:
    """Updates the live guild count for the bots bots.ondiscord.xyz page."""
    logging.info(f"Sending a guild_count of {guild_count} to BOD")

    async with aiohttp.ClientSession() as session:
        await session.post(
            BOD_URL, json={"guildCount": guild_count}, headers=BOD_HEADERS
        )
