from typing import Callable, Dict

from . import apis
from . import config
from . import embeds
from .consts import NotificationType


def req_id_owner(func: Callable) -> Callable:
    """A function wrapper that only runs the wrapped function if
    kwargs["message"].author.id == config.BOT_OWNER_ID.

    The wrapped function will return None if message.author does not meet requirements.
    """

    def wrapper(**kwargs):
        message = kwargs["message"]
        if message.author.id == config.BOT_OWNER_ID:
            return func(**kwargs)
        return None

    return wrapper


def req_perm_admin(func: Callable) -> Callable:
    """A function wrapper that only runs the wrapped function if
    kwargs["message"].author has the administrator permission.

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
        return embeds.API_ERROR_EMBED
    else:
        return await embeds.create_launch_schedule_embed(next_launch_dict)


@req_id_owner
async def _add(**kwargs):
    client, message, operands = kwargs["client"], kwargs["message"], kwargs["operands"]
    notif_type_str, notif_mentions = operands[0], operands[1:]

    try:
        notif_type = NotificationType[notif_type_str]
    except KeyError:
        return "Invalid notification type"

    if (
        client.ds.add_subbed_channel(message.channel.id, notif_type, notif_mentions)
        is False
    ):
        return "This channel is already subscribed to the notification service"
    return "This channel has been added to the notification service"


@req_id_owner
async def _remove(**kwargs):
    client, message = kwargs["client"], kwargs["message"]
    if client.ds.remove_subbed_channel(message.channel.id) is False:
        return "This channel was not previously subscribed to the notification service"
    return "This channel has been removed from the notification service"


async def _info(**kwargs):
    client = kwargs["client"]
    guild_count = len(client.guilds)
    sub_count = client.ds.subbed_channels_count()
    return embeds.create_bot_info_embed(guild_count, sub_count)


async def _help(**kwargs):
    return embeds.HELP_EMBED


@req_id_owner
async def _debug_launching_soon(**kwargs):
    """Send launching soon embed for the given launch.
    """
    try:
        launch_number = int("".join(kwargs["operands"]))
    except ValueError:
        return "Invalid launch number"

    launch_dict = await apis.spacex.get_launch_dict(launch_number)
    if launch_dict == {}:
        return "API returned {}"
    return await embeds.create_launching_soon_embed(launch_dict)


@req_id_owner
async def _debug_launch_information(**kwargs):
    """Send launch information embed for the given launch.
    """
    try:
        launch_number = int("".join(kwargs["operands"]))
    except ValueError:
        return "Invalid launch number"

    launch_dict = await apis.spacex.get_launch_dict(launch_number)
    if launch_dict == {}:
        return "API returned {}"
    return await embeds.create_launch_schedule_embed(launch_dict)


@req_id_owner
async def _reset_notification_task_store(**kwargs):
    """Reset notification_task_store to default values (will trigger new notifications).
    """
    client = kwargs["client"]
    client.ds.set_notification_task_vars(False, {})
    return "Reset using `set_notification_task_vars(False, {})`"


@req_id_owner
async def _shutdown(**kwargs):
    client = kwargs["client"]
    await client.shutdown()


CMD_LOOKUP: Dict[str, Callable] = {
    "nextlaunch": _next_launch,
    "add": _add,
    "remove": _remove,
    "info": _info,
    "help": _help,
    "dbgls": _debug_launching_soon,
    "dbgli": _debug_launch_information,
    "resetnts": _reset_notification_task_store,
    "shutdown": _shutdown,
}
