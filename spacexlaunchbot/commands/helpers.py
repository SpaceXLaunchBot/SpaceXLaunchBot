from typing import Callable

from .. import config


async def _return_none() -> None:
    return None


def _req_id_owner(func: Callable) -> Callable:
    """A function wrapper that only runs the wrapped function if
    kwargs["message"].author.id == config.BOT_OWNER_ID.

    The wrapped function will return None if message.author does not meet requirements.
    """

    def wrapper(**kwargs):
        message = kwargs["message"]
        if message.author.id == config.BOT_OWNER_ID:
            return func(**kwargs)
        return _return_none()

    return wrapper


def _req_perm_admin(func: Callable) -> Callable:
    """A function wrapper that only runs the wrapped function if
    kwargs["message"].author has the administrator permission.

    The wrapped function will return None if message.author does not meet requirements.
    """

    def wrapper(**kwargs):
        message = kwargs["message"]
        perms = message.author.guild_permissions
        if getattr(perms, "administrator", False):
            return func(**kwargs)
        return _return_none()

    return wrapper
