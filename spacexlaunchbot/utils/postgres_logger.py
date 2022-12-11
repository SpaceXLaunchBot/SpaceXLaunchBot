import asyncio
import logging

import asyncpg


class PostgresLogger(logging.StreamHandler):
    def __init__(
        self, fmt: str, loop: asyncio.AbstractEventLoop, db_pool: asyncpg.Pool
    ):
        logging.StreamHandler.__init__(self)
        self.formatter = logging.Formatter(fmt=fmt)
        self.loop = loop
        self.db_pool = db_pool

    async def fire(self, formatted):
        """Shoot our record at Postgres, don't really care if it fails."""
        try:
            time, level, location, function, message = formatted.split(" | ")
            sql = """
            insert into log
                (time, level, location, function, message)
            values
                ($1, $2, $3, $4, $5);"""
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    sql,
                    time,
                    level,
                    location,
                    function,
                    message,
                )
        except ValueError:
            # Not a log that fits our custom format.
            pass

    def emit(self, record):
        # Bare except just seems to be the done thing for custom loggers.
        # pylint: disable=bare-except
        try:
            msg = self.format(record)
            self.loop.create_task(self.fire(msg))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
