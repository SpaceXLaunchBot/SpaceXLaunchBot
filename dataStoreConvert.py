"""A small script to convert the old data store format to the new one."""

import logging
import pickle  # nosec
from copy import deepcopy
from typing import Tuple, Set, Dict, Any, Union

import discord

from spacexlaunchbot.config import PICKLE_DUMP_LOCATION, API_TOKEN_DISCORD
from spacexlaunchbot.notifications import NotificationType
from spacexlaunchbot.storage import DataStore


class OldDataStore:
    def __init__(self, save_file_location: str):
        self._dump_loc = save_file_location

        self._subscribed_channels: Set[int] = set()
        self._launching_soon_notif_sent: bool = False
        self._launch_information_embed_dict: Dict = {}
        self._guild_options: Dict[int, Dict[str, Any]] = {}

        try:
            with open(self._dump_loc, "rb") as f_in:
                tmp = pickle.load(f_in)  # nosec
            logging.info("Loaded from disk")
            self.__dict__.update(tmp)
        except FileNotFoundError:
            pass

    def save(self) -> None:
        pass

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


class TestClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Ready")

        print("Initializing both datastores")
        oldDs = OldDataStore(PICKLE_DUMP_LOCATION)
        newDs = DataStore(PICKLE_DUMP_LOCATION + ".new")

        oldSubbedIds = oldDs.get_subbed_channels()
        print(f"Processing {len(oldSubbedIds)} ids")
        for cid in oldSubbedIds:
            print(f"Processing {cid}")
            channel = self.get_channel(cid)
            if channel is None:
                continue

            guild_id = channel.guild.id
            oldOpts = oldDs.get_guild_options(guild_id)
            mentions = oldOpts.get("mentions", "") if oldOpts is not None else ""
            print(f"with mentions {mentions}")
            newDs.add_subbed_channel(cid, NotificationType.all, mentions)

        newDs.save()


print("Logging into discord")
client = TestClient()
client.run(API_TOKEN_DISCORD)
