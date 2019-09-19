import datetime
from typing import Union, Dict

from aioinflux import InfluxDBClient

import config


class InfluxClient(InfluxDBClient):

    KEY_GUILD_COUNT = "guild_count"
    KEY_SUBSCRIBED_CHANNELS_COUNT = "subscribed_channels_count"
    KEY_COMMAND_USAGE = "command_usage"

    def __init__(self, db: str) -> None:
        super().__init__(db=db)

    async def init_defaults(self):
        # This will not erase if already created
        await self.query(f'CREATE DATABASE "{self.db}"')

    @staticmethod
    def create_point(
        measurement: str, value: int, tags: Union[Dict, None] = None
    ) -> Dict:
        """Create a data point to write to the database

        Args:
            measurement: The name of the value, e.g. "guild_count"
            value: The value, e.g. 100
            tags: A dictionary of tags, e.g. {"host": "server01", "region": "us-west"}

        Returns:
            A dictionary to be written to the database

        """
        if tags is None:
            tags = {}
        return {
            "time": datetime.datetime.now().isoformat(),
            "measurement": measurement,
            "tags": tags,
            "fields": {"value": value},
        }

    async def send_guild_count(self, guild_count: int) -> None:
        point = self.create_point(self.KEY_GUILD_COUNT, guild_count)
        await self.write(point)

    async def send_subscribed_channels_count(self, channel_count: int) -> None:
        point = self.create_point(self.KEY_SUBSCRIBED_CHANNELS_COUNT, channel_count)
        await self.write(point)

    async def send_command_used(self, command_name: str) -> None:
        point = self.create_point(
            self.KEY_COMMAND_USAGE, 1, {"command_name": command_name}
        )
        await self.write(point)


influx = InfluxClient(config.INFLUX_DB)
