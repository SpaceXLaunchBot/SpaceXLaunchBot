import aiohttp, logging


class DblApi:
    """Handles interactions with the discordbots.org API
    """

    def __init__(self, client_id, dbl_token):
        self.log = logging.getLogger(__name__)
        self.dblURL = f"https://discordbots.org/api/bots/{client_id}/stats"
        self.headers = {"Authorization": dbl_token, "Content-Type": "application/json"}

    async def update_guild_count(self, guild_count):
        self.log.info(f"Sending a guild_count of {guild_count} to DBL")
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.dblURL, json={"server_count": guild_count}, headers=self.headers
            )
