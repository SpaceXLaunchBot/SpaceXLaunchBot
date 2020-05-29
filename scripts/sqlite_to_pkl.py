"""Converts the old sqlite data store to the new pickled Python object one.

Takes "slb.sqlite" in the current dir and outputs "slb.pkl".
Requires sqlitedict to be installed.
"""

# fmt: off
import sys; sys.path.insert(0, "../spacexlaunchbot")  # fmt: on
import storage
from sqlitedict import SqliteDict
from typing import Tuple, Set, Dict


class SqliteDb:

    KEY_PREFIX = "slb:"
    KEY_SUBSCRIBED_CHANNELS = KEY_PREFIX + "subscribed_channels"
    KEY_NOTIFICATION_TASK_STORE = KEY_PREFIX + "notification_task_store"
    KEY_GUILD = KEY_PREFIX + "guild:{}"

    def __init__(self, sqlite_location: str):
        self.sqlite = SqliteDict(sqlite_location, autocommit=False)

    def init_defaults(self) -> None:
        if self.KEY_NOTIFICATION_TASK_STORE not in self.sqlite:
            self.sqlite[self.KEY_NOTIFICATION_TASK_STORE] = [False, ""]

        if self.KEY_SUBSCRIBED_CHANNELS not in self.sqlite:
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = set()

        self.sqlite.commit()

    def get_notification_task_store(self) -> Tuple[bool, Dict]:
        return self.sqlite[self.KEY_NOTIFICATION_TASK_STORE]

    def set_notification_task_store(
        self, ls_notif_sent: bool, li_embed_dict: Dict
    ) -> None:
        self.sqlite[self.KEY_NOTIFICATION_TASK_STORE] = [ls_notif_sent, li_embed_dict]
        self.sqlite.commit()

    def set_guild_mentions(self, guild_id: int, to_mention: str) -> None:
        self.sqlite[self.KEY_GUILD.format(guild_id)] = to_mention
        self.sqlite.commit()

    def get_guild_mentions(self, guild_id: int) -> str:
        return self.sqlite.get(self.KEY_GUILD.format(guild_id), "")

    def delete_guild_mentions(self, guild_id: int) -> int:
        if self.KEY_GUILD.format(guild_id) in self.sqlite:
            del self.sqlite[self.KEY_GUILD.format(guild_id)]
            self.sqlite.commit()
            return 1
        return 0

    def get_subbed_channels(self) -> Set[int]:
        return self.sqlite[self.KEY_SUBSCRIBED_CHANNELS]

    def add_subbed_channel(self, channel_id: int) -> int:
        channels = self.sqlite[self.KEY_SUBSCRIBED_CHANNELS]
        if channel_id not in channels:
            channels.add(channel_id)
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = channels
            self.sqlite.commit()
            return 1
        return 0

    def remove_subbed_channel(self, channel_id: int) -> int:
        channels = self.sqlite[self.KEY_SUBSCRIBED_CHANNELS]
        if channel_id in channels:
            channels.remove(channel_id)
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = channels
            self.sqlite.commit()
            return 1
        return 0

    def remove_subbed_channels(self, channels_to_remove: Set[int]) -> None:
        self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] = (
            self.sqlite[self.KEY_SUBSCRIBED_CHANNELS] - channels_to_remove
        )
        self.sqlite.commit()

    def subbed_channels_count(self) -> int:
        return len(self.sqlite[self.KEY_SUBSCRIBED_CHANNELS])

    def stop(self):
        self.sqlite.commit()
        self.sqlite.close()


newDs = storage.DataStore("./slb.pkl")
oldDb = SqliteDb("./slb.sqlite")

subscribed_channels = oldDb.get_subbed_channels()

for chan in subscribed_channels:
    newDs.add_subbed_channel(chan)

launching_soon_notif_sent, launch_information_embed_dict = oldDb.get_notification_task_store()
newDs.set_notification_task_vars(launching_soon_notif_sent, launch_information_embed_dict)

guild_options = {}
for key in oldDb.sqlite:
    if key.startswith("slb:guild:"):
        id = int(key.split("slb:guild:")[1])
        mentions = oldDb.get_guild_mentions(id)
        newDs.set_guild_option(id, "mentions", mentions)

newDs.save()
