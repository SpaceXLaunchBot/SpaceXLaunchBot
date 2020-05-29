import pickle  # nosec
from copy import deepcopy
from typing import Tuple, Set, Dict, Any, Union
import logging


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

        self._subscribed_channels: Set[int] = set()
        self._launching_soon_notif_sent: bool = False
        self._launch_information_embed_dict: Dict = {}
        self._guild_options: Dict[int, Dict[str, Any]] = {}

        try:
            with open(self._dump_loc, "rb") as f_in:
                tmp = pickle.load(f_in)  # nosec
            logging.info(f"Loaded from disk: {tmp=}")
            self.__dict__.update(tmp)
        except FileNotFoundError:
            pass

    def save(self) -> None:
        # Idea from https://stackoverflow.com/a/2842727/6396652.
        to_dump = {
            "_subscribed_channels": self._subscribed_channels,
            "_launching_soon_notif_sent": self._launching_soon_notif_sent,
            "_launch_information_embed_dict": self._launch_information_embed_dict,
            "_guild_options": self._guild_options,
        }
        with open(self._dump_loc, "wb") as f_out:
            pickle.dump(to_dump, f_out, protocol=pickle.HIGHEST_PROTOCOL)

    def get_notification_task_vars(self) -> Tuple[bool, Dict]:
        return (
            self._launching_soon_notif_sent,
            deepcopy(self._launch_information_embed_dict),
        )

    def set_notification_task_vars(
        self, ls_notif_sent: bool, li_embed_dict: Dict
    ) -> None:
        self._launching_soon_notif_sent = ls_notif_sent
        self._launch_information_embed_dict = deepcopy(li_embed_dict)

    def set_guild_option(self, guild_id: int, option: str, value: Any) -> None:
        if guild_id in self._guild_options:
            self._guild_options[guild_id][option] = value
        else:
            self._guild_options[guild_id] = {option: value}

    def get_guild_options(self, guild_id: int) -> Union[None, Dict[str, Any]]:
        if guild_id in self._guild_options:
            return deepcopy(self._guild_options[guild_id])
        return None

    def get_all_guilds_options(self) -> Dict[int, Dict[str, Any]]:
        return deepcopy(self._guild_options)

    def remove_guild_options(self, guild_id: int) -> bool:
        if self._guild_options.get(guild_id) is not None:
            del self._guild_options[guild_id]
            return True
        return False

    def add_subbed_channel(self, channel_id: int) -> bool:
        if channel_id not in self._subscribed_channels:
            self._subscribed_channels.add(channel_id)
            return True
        return False

    def get_subbed_channels(self) -> Set[int]:
        return deepcopy(self._subscribed_channels)

    def remove_subbed_channel(self, channel_id: int) -> bool:
        if channel_id in self._subscribed_channels:
            self._subscribed_channels.remove(channel_id)
            return True
        return False

    def remove_subbed_channels(self, channels_to_remove: Set[int]) -> None:
        self._subscribed_channels = self._subscribed_channels - channels_to_remove

    def subbed_channels_count(self) -> int:
        return len(self._subscribed_channels)
