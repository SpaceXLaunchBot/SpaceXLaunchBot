import logging

import aiohttp

import config

bot_lists = {
    "bod": {
        "url": f"https://bots.ondiscord.xyz/bot-api/bots/{config.BOT_CLIENT_ID}/guilds",
        "token": config.API_TOKEN_BOT_LIST_BOD,
        "guild_count_parameter": "guildCount",
    },
    "dbl": {
        "url": f"https://top.gg/api/bots/{config.BOT_CLIENT_ID}/stats",
        "token": config.API_TOKEN_BOT_LIST_DBL,
        "guild_count_parameter": "server_count",
    },
    "dbg": {
        "url": f"https://discord.bots.gg/api/v1/bots/{config.BOT_CLIENT_ID}/stats",
        "token": config.API_TOKEN_BOT_LIST_DBG,
        "guild_count_parameter": "guildCount",
    },
    "bfd": {
        "url": f"https://botsfordiscord.com/api/bot/{config.BOT_CLIENT_ID}",
        "token": config.API_TOKEN_BOT_LIST_BFD,
        "guild_count_parameter": "server_count",
    },
}


async def post_count_to_bot_list(
    name: str, guild_count: int, url: str, token: str, guild_count_parameter: str
) -> None:
    logging.info(f"Sending a guild_count of {guild_count} to {name}")

    async with aiohttp.ClientSession() as session:
        await session.post(
            url,
            json={guild_count_parameter: guild_count},
            headers={"Authorization": token, "Content-Type": "application/json"},
        )


async def post_all_bot_lists(guild_count: int) -> None:
    for bot_list in bot_lists:
        await post_count_to_bot_list(
            bot_list,
            guild_count,
            bot_lists[bot_list]["url"],
            bot_lists[bot_list]["token"],
            bot_lists[bot_list]["guild_count_parameter"],
        )
