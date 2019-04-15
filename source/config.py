from os import environ

# Load from environment variables
DISCORD_TOKEN = environ["SpaceXLaunchBotToken"]
DBL_TOKEN = environ["dblToken"]

# Discord ID of the person running the bot
OWNER_ID = "263412940869206027"

# The prefix needed to activate a command
COMMAND_PREFIX = "!"

# The interval time, in minutes, between checking the SpaceX API for updates
API_CHECK_INTERVAL = 15

# How far into the future to look for launches that are happening soon (in minutes)
# Should be more >1 as the launching soon notification task is run every minute
LAUNCHING_SOON_DELTA = 30

# Log settings
LOG_PATH = "/var/log/SLB/bot.log"
LOG_FORMAT = "%(asctime)s : %(levelname)s : %(name)s.%(funcName)s : %(message)s"

# Colours used for different situations
EMBED_COLOURS = {"errorRed": [255, 0, 0], "falconRed": [238, 15, 70]}

# The "game" the bot is playing
BOT_GAME = "with rockets"
