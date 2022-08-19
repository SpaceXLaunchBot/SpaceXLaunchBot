from . import config, discordclient, utils


def main() -> None:
    utils.setup_logging()
    # TODO: Custom formatter for discord logging
    client = discordclient.SpaceXLaunchBotClient()
    client.run(config.API_TOKEN_DISCORD, log_level=config.LOG_LEVEL)


if __name__ == "__main__":
    main()
