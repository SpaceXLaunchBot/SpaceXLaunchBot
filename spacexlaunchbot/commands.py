from aredis import RedisError
import logging

import config, embedcreators, statics
from redisclient import redis
from apis import spacex

log = logging.getLogger(__name__)


async def _from_owner(message):
    """Returns True/False depending on the sender of the message
    """
    return message.author.id == int(config.BOT_OWNER_ID)


async def _from_admin(message):
    """Returns True/False depending on the sender of the message
    """
    try:
        # TODO: Check latest docs for this
        is_admin = message.author.permissions_in(message.channel).administrator
    except AttributeError:
        # AttributeError occurs if user has no roles
        is_admin = False
    return is_admin


async def _next_launch(client, message):
    next_launch_dict = await spacex.get_next_launch_dict()
    if next_launch_dict == -1:
        launch_info_embed = statics.api_error_embed
    else:
        launch_info_embed = await embedcreators.get_launch_info_embed(next_launch_dict)
    await client.safe_send(message.channel, launch_info_embed)


async def _add_channel(client, message):
    if not _from_admin(message):
        return
    reply = "This channel has been added to the notification service"
    added = await redis.sadd(
        "slb.subscribed_channels", str(message.channel.id).encode("UTF-8")
    )
    if added == 0:
        reply = "This channel is already subscribed to the notification service"
    await client.safe_send(message.channel, reply)


async def _remove_channel(client, message):
    if not _from_admin(message):
        return
    reply = "This channel has been removed from the launch notification service"
    removed = await redis.srem(
        "slb.subscribed_channels", str(message.channel.id).encode("UTF-8")
    )
    if removed == 0:
        reply = "This channel was not previously subscribed to the launch notification service"
    await client.safe_send(message.channel, reply)


async def _set_mentions(client, message):
    if not _from_admin(message):
        return
    reply = "Invalid input for setmentions command"
    roles_to_mention = " ".join(message.content.split("setmentions")[1:])
    if roles_to_mention.strip() != "":
        reply = f"Added notification ping for mentions(s): {roles_to_mention}"
        await redis.set_guild_mentions(message.guild.id, roles_to_mention)
    await client.safe_send(message.channel, reply)


async def _get_mentions(client, message):
    if not _from_admin(message):
        return
    reply = "This guild has no mentions set"

    mentions = await redis.get_guild_mentions(message.guild.id)
    if mentions:
        reply = f"Mentions for this guild: {mentions}"

    await client.safe_send(message.channel, reply)


async def _remove_mentions(client, message):
    if not _from_admin(message):
        return
    reply = "Removed mentions succesfully"

    deleted = await redis.delete_guild_mentions(message.guild.id)
    if deleted == 0:
        reply = "This guild has no mentions to be removed"

    await client.safe_send(message.channel, reply)


async def _info(client, message):
    info_embed = await embedcreators.get_info_embed()
    await client.safe_send(message.channel, info_embed)


async def _help(client, message):
    await client.safe_send(message.channel, statics.help_embed)


async def _debug_launching_soon(client, message):
    """Send launching soon embed for prev launch
    """
    if not _from_owner(message):
        return
    next_launch_dict = await spacex.get_next_launch_dict(previous=True)
    lse = await embedcreators.get_launching_soon_embed(next_launch_dict)
    await client.safe_send(message.channel, lse)


async def _reset_notif_task_store(client, message):
    """Reset notification_task_store to default values (triggers notifications)
    """
    if not _from_owner(message):
        return
    await redis.set_notification_task_store("False", statics.general_error_embed)
    await client.safe_send(message.channel, "Reset notification_task_store")


async def _log_dump(client, message):
    """Reply with latest lines from bot.log
    """
    if not _from_owner(message):
        return
    log_message = "```\n{}```"

    with open(config.LOG_PATH, "r") as f:
        # Code block markdown in log_message takes up 7 of the 2k allowed chars
        log_content = f.read()[-(2000 - 7) :]

    await client.safe_send(message.channel, log_message.format(log_content))


# Construct after definitions
cmd_prefix = config.BOT_COMMAND_PREFIX
commands = {
    f"{cmd_prefix}nextlaunch": _next_launch,
    f"{cmd_prefix}addchannel": _add_channel,
    f"{cmd_prefix}removechannel": _remove_channel,
    f"{cmd_prefix}setmentions": _set_mentions,
    f"{cmd_prefix}getmentions": _get_mentions,
    f"{cmd_prefix}removementions": _remove_mentions,
    f"{cmd_prefix}info": _info,
    f"{cmd_prefix}help": _help,
    f"{cmd_prefix}dbgls": _debug_launching_soon,
    f"{cmd_prefix}resetnts": _reset_notif_task_store,
    f"{cmd_prefix}logdump": _log_dump,
}


async def handle_command(client, message):
    # Commands can be in any case
    message.content = message.content.lower()

    # Must be a space in inbetween the command and the paramter(s)
    used_command = message.content.split(" ")[0]

    try:
        command_function = commands[used_command]
        command_function(client, message)
    except KeyError as e:
        pass  # Not a command
    except RedisError as e:
        log.error(f"RedisError occurred: {e}")
        await client.safe_send(message.channel, statics.db_error_embed)
