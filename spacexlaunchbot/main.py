import asyncio
import logging
import aredis
import sys

import structure
import config
import discordclient
import redisclient


async def startup():
    await structure.setup_logging()
    try:
        await redisclient.REDIS.init_defaults()
    except aredis.exceptions.ConnectionError:
        logging.error("Cannot connect to Redis, exiting")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(startup())

    CLIENT = discordclient.SpaceXLaunchBotClient()
    CLIENT.run(config.API_TOKEN_DISCORD)
