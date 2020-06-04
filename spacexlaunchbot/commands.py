from typing import Callable, Dict

import apis
import config
import embeds


def req_id_owner(func: Callable) -> Callable:
    """A function wrapper that only runs the wrapped function if
    message.author.id == BOT_OWNER_ID.

    The wrapped function will return None if message.author does not meet requirements.
    """

    def wrapper(**kwargs):
        message = kwargs["message"]
        if message.author.id == config.BOT_OWNER_ID:
            return func(**kwargs)
        return None

    return wrapper


def req_perm_admin(func: Callable) -> Callable:
    """A function wrapper that only runs the wrapped function if message.author has the
    administrator permission.

    The wrapped function will return None if message.author does not meet requirements.
    """

    def wrapper(**kwargs):
        message = kwargs["message"]
        perms = message.author.permissions_in(message.channel)
        if getattr(perms, "administrator", False):
            return func(**kwargs)
        return None

    return wrapper


async def _next_launch(**kwargs):
    next_launch_dict = await apis.spacex.get_launch_dict()

    if next_launch_dict == {}:
        launch_info_embed = embeds.API_ERROR_EMBED
    else:
        launch_info_embed = await embeds.get_launch_info_embed(next_launch_dict)

    return launch_info_embed


@req_perm_admin
async def _add_channel(**kwargs):
    client = kwargs["client"]
    message = kwargs["message"]
    reply = "This channel has been added to the notification service"

    if client.ds.add_subbed_channel(message.channel.id) is False:
        reply = "This channel is already subscribed to the notification service"

    return reply


@req_perm_admin
async def _remove_channel(**kwargs):
    client = kwargs["client"]
    message = kwargs["message"]
    reply = "This channel has been removed from the notification service"

    if client.ds.remove_subbed_channel(message.channel.id) is False:
        reply = "This channel was not previously subscribed to the notification service"

    return reply


@req_perm_admin
async def _set_mentions(**kwargs):
    client = kwargs["client"]
    message = kwargs["message"]
    reply = "Invalid input for setmentions command"

    roles_to_mention = " ".join(message.content.split("setmentions")[1:])
    roles_to_mention = roles_to_mention.strip()

    if roles_to_mention != "":
        reply = f"Added notification ping for mentions(s): {roles_to_mention}"
        client.ds.set_guild_option(message.guild.id, "mentions", roles_to_mention)

    return reply


@req_perm_admin
async def _get_mentions(**kwargs):
    client = kwargs["client"]
    message = kwargs["message"]
    reply = "This guild has no mentions set"

    if (opts := client.ds.get_guild_options(message.guild.id)) is not None:
        if (mentions := opts.get("mentions")) is not None:
            reply = f"Mentions for this guild: {mentions}"

    return reply


@req_perm_admin
async def _remove_mentions(**kwargs):
    client = kwargs["client"]
    message = kwargs["message"]
    reply = "Removed mentions successfully"

    if client.ds.remove_guild_options(message.guild.id) is False:
        reply = "This guild has no mentions to be removed"

    return reply


async def _info(**kwargs):
    client = kwargs["client"]
    guild_count = len(client.guilds)
    sub_count = client.ds.subbed_channels_count()
    info_embed = await embeds.get_info_embed(guild_count, sub_count)
    return info_embed


async def _help(**kwargs):
    return embeds.HELP_EMBED


@req_id_owner
async def _debug_launching_soon(**kwargs):
    """Send launching soon embed for the given launch.
    """
    message = kwargs["message"]

    try:
        launch_number = "".join(message.content.split(" ")[1:])
        launch_number = int(launch_number)
    except ValueError:
        return "Invalid launch number"

    launch_dict = await apis.spacex.get_launch_dict(launch_number)

    if launch_dict == {}:
        return

    lse = await embeds.get_launching_soon_embed(launch_dict)
    return lse


@req_id_owner
async def _debug_launch_information(**kwargs):
    """Send launch information embed for the given launch.
    """
    message = kwargs["message"]

    try:
        launch_number = "".join(message.content.split(" ")[1:])
        launch_number = int(launch_number)
    except ValueError:
        return "Invalid launch number"

    launch_dict = await apis.spacex.get_launch_dict(launch_number)

    if launch_dict == {}:
        return

    lie = await embeds.get_launch_info_embed(launch_dict)
    return lie


@req_id_owner
async def _reset_notif_task_store(**kwargs):
    """Reset notification_task_store to default values (triggers notifications).
    """
    client = kwargs["client"]
    client.ds.set_notification_task_vars(False, {})
    return "Reset notification_task_store"


@req_id_owner
async def _shutdown(**kwargs):
    client = kwargs["client"]
    await client.shutdown()


CMD_LOOKUP: Dict[str, Callable] = {
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
    "shutdown": _shutdown,
}
