import pytest

import utils


@pytest.mark.asyncio
async def test_utc_from_ts():
    assert await utils.utc_from_ts(None) == "To Be Announced"
    assert await utils.utc_from_ts(0) == "1970-01-01 00:00:00 UTC"
    assert await utils.utc_from_ts(946684800) == "2000-01-01 00:00:00 UTC"
    assert await utils.utc_from_ts(1577836800) == "2020-01-01 00:00:00 UTC"
