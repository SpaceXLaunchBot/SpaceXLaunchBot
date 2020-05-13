import config
import discordclient
import utils
from sqlitedb import db


def main() -> None:
    utils.setup_logging()
    db.init_defaults()
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
