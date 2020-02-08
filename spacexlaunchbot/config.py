import logging
import os

INSIDE_DOCKER = os.environ.get("INSIDE_DOCKER", False)
DOCKER_VOLUME_NAME = "/docker-volume/"

API_TOKEN_DISCORD = os.environ["SLB_API_TOKEN_DISCORD"]

DEFAULT_BL_TOKEN = "test-token-pls-ignore"
API_TOKEN_BOT_LIST_DBL = os.environ.get("SLB_API_TOKEN_BOT_LIST_DBL", DEFAULT_BL_TOKEN)
API_TOKEN_BOT_LIST_BOD = os.environ.get("SLB_API_TOKEN_BOT_LIST_BOD", DEFAULT_BL_TOKEN)
API_TOKEN_BOT_LIST_DBG = os.environ.get("SLB_API_TOKEN_BOT_LIST_DBG", DEFAULT_BL_TOKEN)
API_TOKEN_BOT_LIST_BFD = os.environ.get("SLB_API_TOKEN_BOT_LIST_BFD", DEFAULT_BL_TOKEN)

BOT_OWNER = "Dragon#0571"
BOT_OWNER_ID = 263412940869206027
BOT_COMMAND_PREFIX = "!"
BOT_GAME = "with rockets"
BOT_GITHUB = "https://github.com/r-spacex/SpaceXLaunchBot"
BOT_CLIENT_ID = 411618411169447950
BOT_INVITE_PERMISSIONS = "19456"

LOG_FORMAT = "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s"
LOG_LEVEL = logging.INFO

SQLITE_LOCATION = DOCKER_VOLUME_NAME + "slb.sqlite" if INSIDE_DOCKER else "./slb.sqlite"

# How many minutes to wait in-between checking the SpaceX API for updates
# This does not take into account time taken to process the data and to send out notifs
NOTIF_TASK_API_INTERVAL = 1

# How many minutes to look into the future for an upcoming launch time
# Must be > NOTIF_TASK_API_INTERVAL else you risk skipping a launch
NOTIF_TASK_LAUNCH_DELTA = 30

# error_red --> used for error embeds
# falcon_red --> used for launch embeds
EMBED_COLOURS = {"error_red": (255, 0, 0), "falcon_red": (238, 15, 70)}
