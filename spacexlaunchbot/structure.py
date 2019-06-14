import logging
import logging.handlers
import datetime

import config


async def utc_from_ts(timestamp):
    """Get a UTC string from a unix timestamp
    Specifically, for getting the launch time, so if timestamp is not an int, returns
    "To Be Announced"
    """
    try:
        formatted_date = datetime.datetime.utcfromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return f"{formatted_date} UTC"
    except TypeError:
        # timestamp is not int
        return "To Be Announced"


async def setup_logging():
    """Setup logging
    These settings will apply to any logging.info, error, debug, etc. call from now on
    This uses logging.basicConfig to setup the logging usage, which means this function
    has to be called before anything else even imports logging, otherwise the
    configuration set by this will not be used
    """
    log_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=config.LOG_PATH, when="W0", backupCount=10, encoding="UTF-8"
    )
    log_file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))

    logging.basicConfig(level=config.LOG_LEVEL, handlers=[log_file_handler])

    # Change discord to only log ERROR level and above
    logging.getLogger("discord").setLevel(logging.ERROR)
