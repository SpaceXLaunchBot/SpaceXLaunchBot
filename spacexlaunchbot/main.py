import asyncio
import logging
import sys

import aredis
from aiohttp import client_exceptions as aiohttp_exceptions

import config
import discordclient
from dbs.redisclient import redis
from dbs.influxclient import influx
import utils


async def startup() -> None:
    await utils.setup_logging()
    try:
        await redis.init_defaults()
        await influx.init_defaults()
    except aredis.exceptions.ConnectionError:
        logging.error("Cannot connect to Redis, exiting")
        sys.exit(1)
    except aiohttp_exceptions.ClientConnectorError:
        logging.error("Cannot connect to InfluxDB, exiting")
        sys.exit(1)


def main() -> None:
    asyncio.get_event_loop().run_until_complete(startup())
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
