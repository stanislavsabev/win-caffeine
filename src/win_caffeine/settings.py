"""Package settings."""
import qdarktheme

from win_caffeine import qt, utils


APP_NAME = "win-caffeine"

WINDOW_FIXED_WIDTH = 280
WINDOW_FIXED_HEIGHT = 220


HOUR = 60
MINUTE = 60
DEFAULT_INTERVAL_SEC = 30
MAX_INT = 2_147_483_647
MIN_INT = -MAX_INT - 1


class Theme:
    DEFAULT_THEME = "light"
    AVAILABLE_THEMES = qdarktheme.get_themes()
    current = "light"


_theme = Theme


def init():
    """Init settings."""
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()


def get_theme():
    return _theme.current


def set_theme(theme):
    if theme not in _theme.AVAILABLE_THEMES:
        raise ValueError(f"Theme {theme} is not available.")
    qdarktheme.setup_theme(theme, default_theme="light")
    if theme == "auto":
        theme = utils.theme_from_palette(qt.QApplication.palette())
    _theme.current = theme


class IconPath:
    @property
    def settings(self):
        return f"assets/settings-{_theme.current}.png"

    @property
    def exit(self):
        return f"assets/exit-door-{_theme.current}.png"

    @property
    def coffee_on(self):
        return f"assets/coffee-on-{_theme.current}.png"

    @property
    def coffee_off(self):
        return f"assets/coffee-off-{_theme.current}.png"
