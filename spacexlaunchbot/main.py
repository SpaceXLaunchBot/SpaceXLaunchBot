import asyncio
import logging
import sys

import aredis

import config
import discordclient
import redisclient
import utils


async def startup() -> None:
    await utils.setup_logging()
    try:
        await redisclient.redis.init_defaults()
    except aredis.exceptions.ConnectionError:
        logging.error("Cannot connect to Redis, exiting")
        sys.exit(1)


def main() -> None:
    asyncio.get_event_loop().run_until_complete(startup())
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
