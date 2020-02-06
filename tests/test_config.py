import config


def test_notif_task_config():
    assert isinstance(config.NOTIF_TASK_API_INTERVAL, int)
    assert isinstance(config.NOTIF_TASK_LAUNCH_DELTA, int)

    assert config.NOTIF_TASK_API_INTERVAL > 0
    assert config.NOTIF_TASK_LAUNCH_DELTA > config.NOTIF_TASK_API_INTERVAL
