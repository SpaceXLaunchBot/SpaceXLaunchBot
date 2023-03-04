import logging
import os

#
# Meta
#

INDEV = os.name == "nt"

WEBSITE_URL = "https://spacexlaunchbot.dev/"

BOT_OWNER_NAME = "Dragon#0571"
# BOT_OWNER_ID = 263412940869206027
BOT_COMMAND_PREFIX = "slb"
BOT_GAME_NAME = "with rockets"
BOT_GITHUB_URL = "https://github.com/r-spacex/SpaceXLaunchBot"
BOT_CLIENT_ID = 412281000140472323 if INDEV else 411618411169447950
# BOT_MENTION_STR = f"<@!{BOT_CLIENT_ID}>"
BOT_INVITE_PERMISSIONS = "2147633152"
BOT_INVITE_URL = (
    "https://discord.com/oauth2/authorize?scope=bot"
    f"&client_id={BOT_CLIENT_ID}&permissions={BOT_INVITE_PERMISSIONS}"
)
BOT_SUPPORT_SERVER_INVITE = "https://discord.gg/j6vbHkYSES"

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

# Seem like sensible defaults, may need tuning if DB is used by other applications.
DB_POOL_MIN_CONNECTIONS = 10
DB_POOL_MAX_CONNECTIONS = 50

#
# Discord & Related APIs
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
        "url": f"https://discords.com/bots/api/bot/{BOT_CLIENT_ID}",
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
# Rate Limits (in minutes)
#

# Currently just used to validate NOTIF_TASK_INTERVAL
API_RATELIMIT_MIN_WAIT_LL2 = 5

#
# Notifications
#

# How many minutes to wait in-between checking for notifications to send
# This does not take into account time taken to process the data and to send out notifs
NOTIF_TASK_INTERVAL = 5

# How many minutes to look into the future for an upcoming launch time
# Must be > NOTIF_TASK_INTERVAL else you risk skipping a launch
NOTIF_TASK_LAUNCH_DELTA = 30


def validate():
    assert DB_POOL_MAX_CONNECTIONS >= DB_POOL_MIN_CONNECTIONS
    assert NOTIF_TASK_INTERVAL >= API_RATELIMIT_MIN_WAIT_LL2
    assert NOTIF_TASK_LAUNCH_DELTA > NOTIF_TASK_INTERVAL
