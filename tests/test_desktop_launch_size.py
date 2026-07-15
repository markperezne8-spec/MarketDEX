from PySide6.QtCore import QRect
from launcher import desktop_launch_size


def test_desktop_launch_size_stays_below_available_1080p_workspace():
    width, height = desktop_launch_size(QRect(0, 0, 1920, 1040))
    assert (width, height) == (1280, 800)
    assert height < 1040


def test_desktop_launch_size_scales_down_for_short_workspace():
    width, height = desktop_launch_size(QRect(0, 0, 1366, 700))
    assert width <= 1366
    assert height <= 700
