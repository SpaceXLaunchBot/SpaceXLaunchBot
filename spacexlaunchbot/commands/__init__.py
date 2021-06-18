from typing import Callable

from . import definitions

COMMAND_LOOKUP: dict[str, Callable] = {
    "nextlaunch": definitions.next_launch,
    "launch": definitions.launch,
    "add": definitions.add,
    "remove": definitions.remove,
    "info": definitions.info,
    "help": definitions.help_cmd,
    "dl": definitions.debug_launch_embed,
    "rn": definitions.reset_notification_task_store,
    "shutdown": definitions.shutdown,
}
