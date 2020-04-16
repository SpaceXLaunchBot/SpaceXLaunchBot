import config
import discordclient
import utils
from sqlitedb import sqlitedb


def main() -> None:
    utils.setup_logging()
    sqlitedb.init_defaults()
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
