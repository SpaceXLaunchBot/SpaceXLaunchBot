import structure
import asyncio
import logging
import aredis

import config
import client
import redisclient


async def startup():
    await structure.setup_logging()
    try:
        await redisclient.redis.init_defaults()
    except aredis.exceptions.ConnectionError:
        logging.error("Cannot connect to Redis, exiting")
        quit()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(startup())

    client = client.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)
