import config
import discordclient
import utils


def main() -> None:
    utils.setup_logging()
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD)


if __name__ == "__main__":
    main()
