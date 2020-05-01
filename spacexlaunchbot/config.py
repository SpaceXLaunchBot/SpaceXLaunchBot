import logging
import os

from discord import Colour

#
# Meta
#

BOT_OWNER = "Dragon#0571"
BOT_OWNER_ID = 263412940869206027
BOT_COMMAND_PREFIX = "slb"
BOT_COMMAND_PREFIX_LEGACY = "!"
BOT_GAME = "with rockets"
BOT_GITHUB = "https://github.com/r-spacex/SpaceXLaunchBot"
BOT_CLIENT_ID = 411618411169447950
BOT_INVITE_PERMISSIONS = "19456"

#
# Docker
#

INSIDE_DOCKER = os.environ.get("INSIDE_DOCKER", False)
DOCKER_VOLUME_NAME = "/docker-volume/"

#
# API
#

API_TOKEN_DISCORD = os.environ["SLB_API_TOKEN_DISCORD"]

DEFAULT_BL_TOKEN = "test-token-pls-ignore"

BOT_LIST_DATA = [
    {
        "url": f"https://bots.ondiscord.xyz/bot-api/bots/{BOT_CLIENT_ID}/guilds",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_BOD", DEFAULT_BL_TOKEN),
        "guild_count_parameter": "guildCount",
    },
    {
        "url": f"https://top.gg/api/bots/{BOT_CLIENT_ID}/stats",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_DBL", DEFAULT_BL_TOKEN),
        "guild_count_parameter": "server_count",
    },
    {
        "url": f"https://discord.bots.gg/api/v1/bots/{BOT_CLIENT_ID}/stats",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_DBG", DEFAULT_BL_TOKEN),
        "guild_count_parameter": "guildCount",
    },
    {
        "url": f"https://botsfordiscord.com/api/bot/{BOT_CLIENT_ID}",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_BFD", DEFAULT_BL_TOKEN),
        "guild_count_parameter": "server_count",
    },
]

#
# Logging
#

LOG_FORMAT = "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s"
LOG_LEVEL = logging.INFO

SQLITE_LOCATION = DOCKER_VOLUME_NAME + "slb.sqlite" if INSIDE_DOCKER else "./slb.sqlite"

#
# Notifications
#

# How many minutes to wait in-between checking the SpaceX API for updates
# This does not take into account time taken to process the data and to send out notifs
NOTIF_TASK_API_INTERVAL = 1

# How many minutes to look into the future for an upcoming launch time
# Must be > NOTIF_TASK_API_INTERVAL else you risk skipping a launch
NOTIF_TASK_LAUNCH_DELTA = 30

#
# Embeds
#


class EmbedColours:
    ERROR_RED = Colour.from_rgb(255, 0, 0)
    FALCON_RED = Colour.from_rgb(238, 15, 70)
    INFO_ORANGE = Colour.from_rgb(200, 74, 0)
