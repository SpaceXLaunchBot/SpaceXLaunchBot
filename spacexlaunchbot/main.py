import structure

structure.setup_logging()

import asyncio, logging, aredis
import config, client, redisclient


async def startup():
    try:
        await redisclient.redis.init_defaults()
    except aredis.exceptions.ConnectionError:
        logging.error("Cannot connect to Redis, exiting")
        quit()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(startup())

    client = client.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)
