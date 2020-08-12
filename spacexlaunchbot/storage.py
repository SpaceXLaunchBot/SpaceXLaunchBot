import logging
import pickle  # nosec
from copy import deepcopy
from typing import Tuple, Dict, Any

from .consts import NotificationType


class DataStore:
    """A simple class to store data. Dynamically loads from pickled file if possible.

    All methods that either return or take mutable objects as parameters make a deep
        copy of said object(s) so that changes cannot be made outside the instance.

    Immutable object reference(s):
     - https://stackoverflow.com/a/23715872/6396652
     - https://stackoverflow.com/a/986145/6396652
    """

    def __init__(self, save_file_location: str):
        self._dump_loc = save_file_location

        # Map of {subscribed channel id: {channel options}}.
        # Supported channel options are currently "type" and "mentions".
        self._subscribed_channels: Dict[int, Dict[str, Any]] = {}
        # Boolean indicating if a notification has been sent for the current schedule,
        self._current_schedule_notification_sent: bool = False
        # A dict of the most previously sent schedule embed (for comparison).
        self._previous_schedule_embed_dict: Dict = {}

        try:
            with open(self._dump_loc, "rb") as f_in:
                tmp = pickle.load(f_in)  # nosec
            self.__dict__.update(tmp)
            logging.info(f"Updated self.__dict__ from {self._dump_loc}")
        except FileNotFoundError:
            logging.info(f"Could not find file at location: {self._dump_loc}")

    def save(self) -> None:
        # Idea from https://stackoverflow.com/a/2842727/6396652.
        to_dump = {
            "_subscribed_channels": self._subscribed_channels,
            "_current_schedule_notification_sent": self._current_schedule_notification_sent,
            "_previous_schedule_embed_dict": self._previous_schedule_embed_dict,
        }
        with open(self._dump_loc, "wb") as f_out:
            pickle.dump(to_dump, f_out, protocol=pickle.HIGHEST_PROTOCOL)

    def get_notification_task_vars(self) -> Tuple[bool, Dict]:
        return (
            self._current_schedule_notification_sent,
            deepcopy(self._previous_schedule_embed_dict),
        )

    def set_notification_task_vars(
        self,
        current_schedule_notification_sent: bool,
        previous_schedule_embed_dict: Dict,
    ) -> None:
        self._current_schedule_notification_sent = current_schedule_notification_sent
        self._previous_schedule_embed_dict = deepcopy(previous_schedule_embed_dict)

    def add_subbed_channel(
        self, channel_id: int, notif_type: NotificationType, launch_mentions: str,
    ) -> bool:
        """Add a channel to subscribed channels.

        Args:
            channel_id: The channel to add.
            notif_type: The type of subscription.
            launch_mentions: The mentions for launch notifications.

        """
        if channel_id not in self._subscribed_channels:
            self._subscribed_channels[channel_id] = {
                "type": notif_type,
                "mentions": launch_mentions,
            }
            return True
        return False

    def get_subbed_channels(self) -> Dict[int, Dict[str, Any]]:
        return deepcopy(self._subscribed_channels)

    def remove_subbed_channel(self, channel_id: int) -> bool:
        if channel_id in self._subscribed_channels:
            del self._subscribed_channels[channel_id]
            return True
        return False

    def subbed_channels_count(self) -> int:
        return len(self._subscribed_channels)
