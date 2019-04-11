"""
All tasks and functions used in those tasks that dont belong anywhere else
"""

import asyncio
import logging
from aredis import RedisError

from modules import apis, embedGenerators
from modules.redisClient import redisConn

logger = logging.getLogger(__name__)

ONE_MINUTE = 60  # Just makes things a little more readable


async def infoUpdaterTask():
    """
    Get latest info and either send out new launch info, and/or launch notifications, or
    do nothing
    """
    try:
        latestinfoEmbed, latestLaunchingSoonEmbed = getLatestEmbedDicts()

        """
        TODO:
        Compare new embeds with old ones, figure out what to send, fix sleep time, rename this task, etc.
        """

    except RedisError as e:
        logger.error(f"Redis operation failed: {type(e).__name__}: {e}")
    except ValueError as e:
        pass  # ValueError happens if nextLaunchJSON == -1, logged in the api function
    finally:
        await asyncio.sleep(ONE_MINUTE)


async def getLatestEmbedDicts():
    """
    Returns infoEmbed and launchingSoonEmbed, in a set, in that order
    """
    nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON()
    if nextLaunchJSON == -1:
        raise ValueError("nextLaunchJSON == -1, cannot generate embeds")
    return (
        embedGenerators.genLaunchInfoEmbeds(nextLaunchJSON),
        embedGenerators.genLaunchingSoonEmbed(nextLaunchJSON),
    )


async def sendLaunchNotifs():
    """
    If a launch is happening soon, send notification messages to subscribed channels
    """
    pass


async def sendLaunchInfoNotifs():
    """
    Update subscribed channels with latest info about a launch (payload, launch time, etc.)
    """
    pass
