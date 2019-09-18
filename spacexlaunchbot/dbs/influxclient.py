import datetime
from typing import Dict

from aioinflux import InfluxDBClient

import config


class InfluxClient(InfluxDBClient):
    def __init__(self, db: str) -> None:
        super().__init__(db=db)

    async def init_defaults(self):
        # This will not erase if already created
        await self.query(f'CREATE DATABASE "{self.db}"')

    @staticmethod
    def create_point(measurement: str, value: int) -> Dict:
        return {
            "time": datetime.datetime.now().isoformat(),
            "measurement": measurement,
            "fields": {"value": value},
        }

    async def update_guild_count(self, guild_count: int) -> None:
        point = self.create_point("guild_count", guild_count)
        await self.write(point)

    async def update_subscribed_channels_count(
        self, subbed_channels_count: int
    ) -> None:
        point = self.create_point("subbed_channels_count", subbed_channels_count)
        await self.write(point)


influx = InfluxClient(config.INFLUX_DB)
