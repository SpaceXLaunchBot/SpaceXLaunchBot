import asyncio

from . import config
from . import discordclient
from . import utils


def main() -> None:
    utils.setup_logging()
    client = discordclient.SpaceXLaunchBotClient()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start(config.API_TOKEN_DISCORD))


if __name__ == "__main__":
    main()
