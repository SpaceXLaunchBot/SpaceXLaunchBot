import logging
import aredis

import config
import embedcreators
import statics
import apis
from redisclient import redis


def _from_owner(message):
    """Returns True/False depending on the sender of the message
    """
    return message.author.id == int(config.BOT_OWNER_ID)


def _from_admin(message):
    """Returns True/False depending on the sender of the message
    """
    try:
        is_admin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        is_admin = False
    return is_admin


async def _next_launch(**kwargs):
    next_launch_dict = await apis.spacex.get_next_launch_dict()

    if next_launch_dict == -1:
        launch_info_embed = statics.API_ERROR_EMBED
    else:
        launch_info_embed = await embedcreators.get_launch_info_embed(next_launch_dict)

    return launch_info_embed


async def _add_channel(**kwargs):
    message = kwargs["message"]
    if not _from_admin(message):
        return

    reply = "This channel has been added to the notification service"

    added = await redis.add_subbed_channel(message.channel.id)
    if added == 0:
        reply = "This channel is already subscribed to the notification service"

    return reply


async def _remove_channel(**kwargs):
    message = kwargs["message"]
    if not _from_admin(message):
        return

    reply = "This channel has been removed from the notification service"

    removed = await redis.remove_subbed_channel(message.channel.id)
    if removed == 0:
        reply = "This channel was not previously subscribed to the notification service"

    return reply


async def _set_mentions(**kwargs):
    message = kwargs["message"]
    if not _from_admin(message):
        return

    reply = "Invalid input for setmentions command"
    roles_to_mention = " ".join(message.content.split("setmentions")[1:])
    roles_to_mention = roles_to_mention.strip()

    if roles_to_mention != "":
        reply = f"Added notification ping for mentions(s): {roles_to_mention}"
        await redis.set_guild_mentions(message.guild.id, roles_to_mention)

    return reply


async def _get_mentions(**kwargs):
    message = kwargs["message"]
    if not _from_admin(message):
        return

    reply = "This guild has no mentions set"

    mentions = await redis.get_guild_mentions(message.guild.id)
    if mentions:
        reply = f"Mentions for this guild: {mentions}"

    return reply


async def _remove_mentions(**kwargs):
    message = kwargs["message"]
    if not _from_admin(message):
        return

    reply = "Removed mentions succesfully"

    deleted = await redis.delete_guild_mentions(message.guild.id)
    if deleted == 0:
        reply = "This guild has no mentions to be removed"

    return reply


async def _info(**kwargs):
    client = kwargs["client"]
    info_embed = await embedcreators.get_info_embed(client)
    return info_embed


async def _help(**kwargs):
    return statics.HELP_EMBED


async def _debug_launching_soon(**kwargs):
    """Send launching soon embed for the given launch
    """
    message = kwargs["message"]
    if not _from_owner(message):
        return

    try:
        launch_number = "".join(message.content.split(" ")[1:])
        launch_number = int(launch_number)
    except ValueError:
        return "Invalid launch number"

    next_launch_dict = await apis.spacex.get_next_launch_dict(launch_number)
    lse = await embedcreators.get_launching_soon_embed(next_launch_dict)
    return lse


async def _debug_launch_information(**kwargs):
    """Send launch information embed for the given launch
    """
    message = kwargs["message"]
    if not _from_owner(message):
        return

    try:
        launch_number = "".join(message.content.split(" ")[1:])
        launch_number = int(launch_number)
    except ValueError:
        return "Invalid launch number"

    next_launch_dict = await apis.spacex.get_next_launch_dict(launch_number)
    lie = await embedcreators.get_launch_info_embed(next_launch_dict)
    return lie


async def _reset_notif_task_store(**kwargs):
    """Reset notification_task_store to default values (triggers notifications)
    prefix + resetnts
    """
    message = kwargs["message"]
    if not _from_owner(message):
        return

    await redis.set_notification_task_store("False", statics.GENERAL_ERROR_EMBED)
    return "Reset notification_task_store"


async def _log_dump(**kwargs):
    """Reply with latest lines from bot.log
    prefix + logdump
    """
    message = kwargs["message"]
    if not _from_owner(message):
        return

    log_message = "```\n{}```"

    with open(config.LOG_PATH, "r") as config_file:
        # Code block markdown in log_message takes up 7 of the 2000 allowed chars
        log_content = config_file.read()[-1993:]

    return log_message.format(log_content)


# Define after commands function definitions
CMD_PREFIX = config.BOT_COMMAND_PREFIX
CMD_FUNC_LOOKUP = {
    f"{CMD_PREFIX}nextlaunch": _next_launch,
    f"{CMD_PREFIX}addchannel": _add_channel,
    f"{CMD_PREFIX}removechannel": _remove_channel,
    f"{CMD_PREFIX}setmentions": _set_mentions,
    f"{CMD_PREFIX}getmentions": _get_mentions,
    f"{CMD_PREFIX}removementions": _remove_mentions,
    f"{CMD_PREFIX}info": _info,
    f"{CMD_PREFIX}help": _help,
    f"{CMD_PREFIX}dbgls": _debug_launching_soon,
    f"{CMD_PREFIX}dbgli": _debug_launch_information,
    f"{CMD_PREFIX}resetnts": _reset_notif_task_store,
    f"{CMD_PREFIX}logdump": _log_dump,
}


async def handle_command(client, message):
    # Commands can be in any case
    message.content = message.content.lower()
    command_used = message.content.split(" ")[0]

    try:
        run_command = CMD_FUNC_LOOKUP[command_used]
        # All commands are passed the client and the message objects
        to_send = await run_command(client=client, message=message)

    except KeyError:
        to_send = None

    except aredis.RedisError as ex:
        logging.error(f"RedisError occurred: {type(ex).__name__}: {ex}")
        to_send = statics.DB_ERROR_EMBED

    if to_send is None:
        return

    await client.send_s(message.channel, to_send)
