import discord

import config
import embedcreators
import statics
import apis
from redisclient import redis


def _from_owner(message: discord.Message) -> bool:
    """Returns True/False depending on the sender of the message
    """
    return message.author.id == config.BOT_OWNER_ID


def _from_admin(message: discord.Message) -> bool:
    """Returns True/False depending on the sender of the message
    """
    try:
        is_admin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        is_admin = False
    return is_admin


async def _next_launch(**kwargs):
    next_launch_dict = await apis.spacex.get_launch_dict()

    if next_launch_dict == {}:
        launch_info_embed = statics.API_ERROR_EMBED
    else:
        launch_info_embed = await embedcreators.get_launch_info_embed(next_launch_dict)

    return launch_info_embed


async def _add_channel(**kwargs):
    message = kwargs.get("message")
    if not _from_admin(message):
        return

    reply = "This channel has been added to the notification service"

    added = await redis.add_subbed_channel(message.channel.id)
    if added == 0:
        reply = "This channel is already subscribed to the notification service"

    return reply


async def _remove_channel(**kwargs):
    message = kwargs.get("message")
    if not _from_admin(message):
        return

    reply = "This channel has been removed from the notification service"

    removed = await redis.remove_subbed_channel(message.channel.id)
    if removed == 0:
        reply = "This channel was not previously subscribed to the notification service"

    return reply


async def _set_mentions(**kwargs):
    message = kwargs.get("message")
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
    message = kwargs.get("message")
    if not _from_admin(message):
        return

    reply = "This guild has no mentions set"

    mentions = await redis.get_guild_mentions(message.guild.id)
    if mentions:
        reply = f"Mentions for this guild: {mentions}"

    return reply


async def _remove_mentions(**kwargs):
    message = kwargs.get("message")
    if not _from_admin(message):
        return

    reply = "Removed mentions succesfully"

    deleted = await redis.delete_guild_mentions(message.guild.id)
    if deleted == 0:
        reply = "This guild has no mentions to be removed"

    return reply


async def _info(**kwargs):
    client = kwargs.get("client")
    info_embed = await embedcreators.get_info_embed(client)
    return info_embed


async def _help(**kwargs):
    return statics.HELP_EMBED


async def _debug_launching_soon(**kwargs):
    """Send launching soon embed for the given launch
    """
    message = kwargs.get("message")
    if not _from_owner(message):
        return

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


async def _debug_launch_information(**kwargs):
    """Send launch information embed for the given launch
    """
    message = kwargs.get("message")
    if not _from_owner(message):
        return

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


async def _reset_notif_task_store(**kwargs):
    """Reset notification_task_store to default values (triggers notifications)
    prefix + resetnts
    """
    message = kwargs.get("message")
    if not _from_owner(message):
        return

    await redis.set_notification_task_store("False", statics.GENERAL_ERROR_EMBED)
    return "Reset notification_task_store"


async def _log_dump(**kwargs):
    """Reply with latest lines from bot.log
    prefix + logdump
    """
    message = kwargs.get("message")
    if not _from_owner(message):
        return

    log_message = "```\n{}```"

    with open(config.LOG_PATH, "r") as config_file:
        # Code block markdown in log_message takes up 7 of the 2000 allowed chars
        log_content = config_file.read()[-1993:]

    return log_message.format(log_content)


CMD_FUNC_LOOKUP = {
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
