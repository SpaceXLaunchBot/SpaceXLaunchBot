import os, logging


# API TOKENS

# Load from environment variables
API_TOKEN_DISCORD = os.environ["SLB_API_TOKEN_DISCORD"]
API_TOKEN_DBL = os.environ["SLB_API_TOKEN_DBL"]


# BOT SETTINGS

# Discord ID of the person running the bot
BOT_OWNER_ID = "263412940869206027"

# The prefix needed to activate a command
BOT_COMMAND_PREFIX = "!"

# The title of the "game" that the bot is playing
BOT_GAME = "with rockets"


# NOTIFICATION TASK SETTINGS

# The interval time, in minutes, between checking the SpaceX API for updates
# This does not take into account time taken to process the data and to send out notifs
NOTIF_TASK_API_INTERVAL = 1

# How many minutes to look into the future for an upcoming launch time
# Must be > NOTIF_TASK_API_INTERVAL else you risk skipping a launch
NOTIF_TASK_LAUNCH_DELTA = 30


# LOG SETTINGS

# Save log in current dir if on win
LOG_PATH = "/var/log/spacexlaunchbot/bot.log" if os.name != "nt" else "bot.log"
LOG_FORMAT = "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s"
LOG_LEVEL = logging.INFO

# EMBED SETTINGS

# Colours used for different situations
# error_red --> used for error embeds
# falcon_red --> used for launch embeds
EMBED_COLOURS = {"error_red": (255, 0, 0), "falcon_red": (238, 15, 70)}


# REDIS SETTINGS

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
