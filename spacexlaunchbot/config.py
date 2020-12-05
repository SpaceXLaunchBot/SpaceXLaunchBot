import logging
import os

#
# Meta
#

BOT_OWNER_NAME = "Dragon#0571"
BOT_OWNER_ID = 263412940869206027
BOT_COMMAND_PREFIX = "slb"
BOT_GAME_NAME = "with rockets"
BOT_GITHUB_URL = "https://github.com/r-spacex/SpaceXLaunchBot"
BOT_CLIENT_ID = 411618411169447950
BOT_INVITE_PERMISSIONS = "19456"
BOT_INVITE_URL = (
    "https://discord.com/oauth2/authorize?scope=bot"
    f"&client_id={BOT_CLIENT_ID}&permissions={BOT_INVITE_PERMISSIONS}"
)

#
# Docker
#

INSIDE_DOCKER = bool(os.environ.get("INSIDE_DOCKER", False))
DOCKER_VOLUME_PATH = "/docker-volume/"

#
# Storage
#

PICKLE_DUMP_LOCATION = DOCKER_VOLUME_PATH + "slb.pkl" if INSIDE_DOCKER else "./slb.pkl"

DB_HOST = os.environ.get("SLB_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("SLB_DB_PORT", 5432))

DB_USER = os.environ.get("POSTGRES_USER", "slb")
DB_PASS = os.environ["POSTGRES_PASSWORD"]
DB_NAME = os.environ.get("POSTGRES_DB", "spacexlaunchbot")

#
# API
#

API_TOKEN_DISCORD = os.environ["SLB_API_TOKEN_DISCORD"]

BOT_LIST_DEFAULT_TOKEN = "test-token-pls-ignore"
BOT_LIST_DATA = [
    {
        "url": f"https://bots.ondiscord.xyz/bot-api/bots/{BOT_CLIENT_ID}/guilds",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_BOD", BOT_LIST_DEFAULT_TOKEN),
        "guild_count_parameter": "guildCount",
    },
    {
        "url": f"https://top.gg/api/bots/{BOT_CLIENT_ID}/stats",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_DBL", BOT_LIST_DEFAULT_TOKEN),
        "guild_count_parameter": "server_count",
    },
    {
        "url": f"https://discord.bots.gg/api/v1/bots/{BOT_CLIENT_ID}/stats",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_DBG", BOT_LIST_DEFAULT_TOKEN),
        "guild_count_parameter": "guildCount",
    },
    {
        "url": f"https://botsfordiscord.com/api/bot/{BOT_CLIENT_ID}",
        "token": os.environ.get("SLB_API_TOKEN_BOT_LIST_BFD", BOT_LIST_DEFAULT_TOKEN),
        "guild_count_parameter": "server_count",
    },
]

#
# Logging
#

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s"
LOG_LEVEL = logging.INFO

#
# Notifications
#

# How many minutes to wait in-between checking the SpaceX API for updates
# This does not take into account time taken to process the data and to send out notifs
NOTIF_TASK_API_INTERVAL = 1

# How many minutes to look into the future for an upcoming launch time
# Must be > NOTIF_TASK_API_INTERVAL else you risk skipping a launch
NOTIF_TASK_LAUNCH_DELTA = 30
