from . import adminclient, config, discordclient, utils


def main() -> None:
    config.validate()
    utils.setup_logging()

    if config.INDEV and not config.INSIDE_DOCKER:
        print(f"\n\n{'!'*10}\n\nADMIN MODE ACTIVE\n\n{'!'*10}\n\n")
        if input("Type 'ok' to continue\n") != "ok":
            return
        client = adminclient.AdminSpaceXLaunchBotClient()
    else:
        client = discordclient.SpaceXLaunchBotClient()

    client.run(config.API_TOKEN_DISCORD, log_handler=None)


if __name__ == "__main__":
    main()
