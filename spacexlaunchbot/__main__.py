from . import config, discordclient, utils


def main() -> None:
    config.validate()
    utils.setup_logging()
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD, log_handler=None)


if __name__ == "__main__":
    main()
