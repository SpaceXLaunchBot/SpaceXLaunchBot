from enum import Enum

from discord import Color


class Colour:
    # pylint: disable=too-few-public-methods
    red_error = Color.from_rgb(255, 0, 0)
    red_falcon = Color.from_rgb(238, 15, 70)
    # orange_info = Color.from_rgb(200, 74, 0)


class NotificationType(Enum):
    all = 0
    schedule = 1
    launch = 2
