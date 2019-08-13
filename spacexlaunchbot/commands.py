from typing import Callable, Dict

import config
import embedcreators
import statics
import apis
from redisclient import redis


def req_id_owner(func: Callable) -> Callable:
    """
    Runs command if message.author.id == BOT_OWNER_ID
    The wrapped function will return None if message.author does not meet requirements

    :param func: The function to wrap
    :return: The wrapped function
    """

    def wrapper(**kwargs):
        message = kwargs.get("message")
        if message.author.id == config.BOT_OWNER_ID:
            return func(**kwargs)
        return None

    return wrapper


def req_perm_admin(func: Callable) -> Callable:
    """
    Runs command if message.author has the administrator permission
    The wrapped function will return None if message.author does not meet requirements

    :param func: The function to wrap
    :return: The wrapped function
    """

    def wrapper(**kwargs):
        message = kwargs.get("message")
        perms = message.author.permissions_in(message.channel)
        if getattr(perms, "administrator", False):
            return func(**kwargs)
        return None

    return wrapper


async def _next_launch(**kwargs):
    next_launch_dict = await apis.spacex.get_launch_dict()

    if next_launch_dict == {}:
        launch_info_embed = statics.API_ERROR_EMBED
    else:
        launch_info_embed = await embedcreators.get_launch_info_embed(next_launch_dict)

    return launch_info_embed


@req_perm_admin
async def _add_channel(**kwargs):
    message = kwargs.get("message")
    reply = "This channel has been added to the notification service"

    added = await redis.add_subbed_channel(message.channel.id)
    if added == 0:
        reply = "This channel is already subscribed to the notification service"

    return reply


@req_perm_admin
async def _remove_channel(**kwargs):
    message = kwargs.get("message")
    reply = "This channel has been removed from the notification service"

    removed = await redis.remove_subbed_channel(message.channel.id)
    if removed == 0:
        reply = "This channel was not previously subscribed to the notification service"

    return reply


@req_perm_admin
async def _set_mentions(**kwargs):
    message = kwargs.get("message")
    reply = "Invalid input for setmentions command"

    roles_to_mention = " ".join(message.content.split("setmentions")[1:])
    roles_to_mention = roles_to_mention.strip()

    if roles_to_mention != "":
        reply = f"Added notification ping for mentions(s): {roles_to_mention}"
        await redis.set_guild_mentions(message.guild.id, roles_to_mention)

    return reply


@req_perm_admin
async def _get_mentions(**kwargs):
    message = kwargs.get("message")
    reply = "This guild has no mentions set"

    mentions = await redis.get_guild_mentions(message.guild.id)
    if mentions:
        reply = f"Mentions for this guild: {mentions}"

    return reply


@req_perm_admin
async def _remove_mentions(**kwargs):
    message = kwargs.get("message")
    reply = "Removed mentions succesfully"

    deleted = await redis.delete_guild_mentions(message.guild.id)
    if deleted == 0:
        reply = "This guild has no mentions to be removed"

    return reply


async def _info(**kwargs):
    client = kwargs.get("client")
    guild_count = len(client.guilds)
    info_embed = await embedcreators.get_info_embed(guild_count)
    return info_embed


async def _help(**kwargs):
    return statics.HELP_EMBED


@req_id_owner
async def _debug_launching_soon(**kwargs):
    """
    Send launching soon embed for the given launch
    """
    message = kwargs.get("message")

    try:
        launch_number = "".join(message.content.split(" ")[1:])
        launch_number = int(launch_number)
    except ValueError:
        return "Invalid launch number"

    launch_dict = await apis.spacex.get_launch_dict(launch_number)

    if launch_dict == {}:
        return

    lse = await embedcreators.get_launching_soon_embed(launch_dict)
    return lse


@req_id_owner
async def _debug_launch_information(**kwargs):
    """
    Send launch information embed for the given launch
    """
    message = kwargs.get("message")

    try:
        launch_number = "".join(message.content.split(" ")[1:])
        launch_number = int(launch_number)
    except ValueError:
        return "Invalid launch number"

    launch_dict = await apis.spacex.get_launch_dict(launch_number)

    if launch_dict == {}:
        return

    lie = await embedcreators.get_launch_info_embed(launch_dict)
    return lie


@req_id_owner
async def _reset_notif_task_store(**kwargs):
    """
    Reset notification_task_store to default values (triggers notifications)
    """
    await redis.set_notification_task_store("False", "0")
    return "Reset notification_task_store"


@req_id_owner
async def _log_dump(**kwargs):
    """
    Tail bot.log and send it
    """
    log_message = "```\n{}```"

    with open(config.LOG_PATH, "r") as config_file:
        # Code block markdown in log_message takes up 7 of the 2000 allowed chars
        log_content = config_file.read()[-1993:]

    return log_message.format(log_content)


CMD_FUNC_LOOKUP: Dict[str, Callable] = {
    "nextlaunch": _next_launch,
    "addchannel": _add_channel,
    "removechannel": _remove_channel,
    "setmentions": _set_mentions,
    "getmentions": _get_mentions,
    "removementions": _remove_mentions,
    "info": _info,
    "help": _help,
    "dbgls": _debug_launching_soon,
    "dbgli": _debug_launch_information,
    "resetnts": _reset_notif_task_store,
    "logdump": _log_dump,
}
