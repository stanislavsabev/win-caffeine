"""App theme."""
import qdarktheme  # type: ignore

from win_caffeine import qt
from win_caffeine import settings
from win_caffeine import utils


class Theme:
    current = settings.DEFAULT_APP_THEME


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


def get_current_theme() -> str:
    return theme.current


def set_theme(name: str, app: qt.QApplication):
    if name not in qdarktheme.get_themes():
        raise ValueError(f"Theme {name} is not available.")
    qdarktheme.setup_theme(name, default_theme="light")
    if name == "auto":
        name = utils.theme_from_palette(app.palette())
    theme.current = name
