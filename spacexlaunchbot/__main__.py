import os

from . import adminclient, config, discordclient, utils


def main() -> None:
    config.validate()
    utils.setup_logging()

    client: discordclient.SpaceXLaunchBotClient | adminclient.AdminSpaceXLaunchBotClient

    if config.INDEV:
        print(f"\n\n{'!' * 10}\n\nADMIN MODE ACTIVE\n\n{'!' * 10}\n\n")
        if os.environ.get("SLB_I_REALLY_PROMISE_I_WANT_TO_ENABLE_ADMIN_PERMISSIONS", False) is False:
            if input("Type 'ok' to continue\n") != "ok":
                return
        client = adminclient.AdminSpaceXLaunchBotClient()
    else:
        client = discordclient.SpaceXLaunchBotClient()

    client.run(config.API_TOKEN_DISCORD, log_handler=None)


if __name__ == "__main__":
    main()
