"""Package settings."""
import qdarktheme

from win_caffeine import qt
from win_caffeine import utils


APP_NAME = "win-caffeine"

WINDOW_FIXED_WIDTH = 280
WINDOW_FIXED_HEIGHT = 280


HOUR = 60
MINUTE = 60
DEFAULT_INTERVAL_SEC = 30
MAX_INT = 2_147_483_647
MIN_INT = -MAX_INT - 1


_AVAILABLE_THEMES = qdarktheme.get_themes()


class Theme:
    DEFAULT_THEME = "light"
    current = "light"


class IconPath:
    @property
    def settings(self) -> str:
        return f"assets/settings-{theme.current}.png"

    @property
    def exit(self) -> str:
        return f"assets/exit-door-{theme.current}.png"

    @property
    def coffee_on(self) -> str:
        return f"assets/coffee-on-{theme.current}.png"

    @property
    def coffee_off(self) -> str:
        return f"assets/coffee-off-{theme.current}.png"


theme = Theme()
icon_path = IconPath()


def init():
    """Init settings."""
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()


def get_current_theme() -> str:
    return theme.current


def set_theme(name: str, app: qt.QApplication):
    if name not in _AVAILABLE_THEMES:
        raise ValueError(f"Theme {name} is not available.")
    qdarktheme.setup_theme(name, default_theme="light")
    if name == "auto":
        name = utils.theme_from_palette(app.palette())
    theme.current = name
