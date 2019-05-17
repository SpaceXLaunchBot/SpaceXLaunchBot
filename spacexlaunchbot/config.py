import os

# Load from environment variables
DISCORD_TOKEN = os.environ["slb_discord_token"]
DBL_TOKEN = os.environ["slb_dbl_token"]

# Discord ID of the person running the bot
OWNER_ID = "263412940869206027"

# The prefix needed to activate a command
COMMAND_PREFIX = "!"

# The interval time, in minutes, between checking the SpaceX API for updates
API_CHECK_INTERVAL = 1

# How many minutes to look into the future for an upcoming launch time
# Must be > API_CHECK_INTERVAL else you risk skipping a launch
LAUNCHING_SOON_DELTA = 30

# Log settings
# Save log in current dir if on win
LOG_PATH = "/var/log/spacexlaunchbot/bot.log" if os.name != "nt" else "bot.log"
LOG_FORMAT = "%(asctime)s : %(levelname)s : %(name)s.%(funcName)s : %(message)s"

# Colours used for different situations
EMBED_COLOURS = {"error_red": (255, 0, 0), "falcon_red": (238, 15, 70)}

# The title of the "game" that the bot is playing
BOT_GAME = "with rockets"

# Redis settings
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
