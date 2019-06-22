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
        await redisclient.redis.init_defaults()
    except aredis.exceptions.ConnectionError:
        logging.error("Cannot connect to Redis, exiting")
        sys.exit(1)


def main():
    asyncio.get_event_loop().run_until_complete(startup())

    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
