from . import config, discordclient, utils


def main() -> None:
    utils.setup_logging()
    client = discordclient.SpaceXLaunchBotClient()
    # no log handler as we set up our own in setup_logging
    client.run(config.API_TOKEN_DISCORD, log_handler=None)


if __name__ == "__main__":
    main()
