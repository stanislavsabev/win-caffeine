"""Util functions."""
from datetime import timedelta

from win_caffeine import qt


def get_time_hh_mm_ss(sec: int):
    # create timedelta and convert it into string
    return str(timedelta(seconds=sec))


def get_icon_path(mode, theme) -> str:
    return f"assets/coffee-{mode}-{theme}.png"


def is_dark_theme(palette: qt.QPalette) -> bool:
    text_color = palette.color(palette.Text)
    lum = sum((text_color.red(), text_color.green(), text_color.blue())) // 3
    return lum > 127


def theme_from_palette(palette) -> str:
    return "dark" if is_dark_theme(palette) else "light"
