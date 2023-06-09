"""Package settings."""
import logging


logger = logging.getLogger(__name__)

APP_NAME = "win-caffeine"

# GUI Settings
WINDOW_FIXED_WIDTH = 280
WINDOW_FIXED_HEIGHT = 280
DEFAULT_APP_THEME = "light"

MULTITHREADING = True
START_IN_SUSPEND_MODE = MULTITHREADING

HOUR = 60
MINUTE = 60
DEFAULT_REFRESH_INTERVAL_SEC = MINUTE
MAX_INT = 2_147_483_647
MIN_INT = -MAX_INT - 1


def init(*args, **kwargs):
    """Init settings."""
    pass
