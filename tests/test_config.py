import config


def test_redis_config():
    assert isinstance(config.REDIS_DB, int)
    assert isinstance(config.REDIS_HOST, str)
    assert isinstance(config.REDIS_PORT, int)


def test_influx_config():
    assert isinstance(config.INFLUX_DB, str)


def test_update_metrics_task_config():
    assert isinstance(config.UPDATE_INFLUXDB_METRICS_TASK_INTERVAL, int)

    assert config.UPDATE_INFLUXDB_METRICS_TASK_INTERVAL > 0


def test_notif_task_config():
    assert isinstance(config.NOTIF_TASK_API_INTERVAL, int)
    assert isinstance(config.NOTIF_TASK_LAUNCH_DELTA, int)

    assert config.NOTIF_TASK_API_INTERVAL > 0
    assert config.NOTIF_TASK_LAUNCH_DELTA > config.NOTIF_TASK_API_INTERVAL
