import asyncio

import config
import discordclient
import utils
from sqlitedb import sqlitedb


async def startup() -> None:
    utils.setup_logging()
    sqlitedb.init_defaults()


def main() -> None:
    asyncio.get_event_loop().run_until_complete(startup())
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
