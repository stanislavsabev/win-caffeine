"""Screen lock implementation."""
import ctypes
import time

from win_caffeine import const

# Define constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


class _State:
    is_on = True
    time_span_min = 0
    refresh_interval_sec = 0


def is_on() -> bool:
    """True if screen lock is NOT prevented."""
    return _state.is_on


def prevent_screen_lock():
    """Prevent screen lock."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    _state.is_on = False


def release_screen_lock():
    """Release screen lock prevention."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    _state.is_on = True


def run_prevent_screen_lock(
    time_span_min: int, refresh_interval_sec: int = const.DEFAULT_INTERVAL_SEC
):
    """Prevent screen lock for amount of time.

    Args:
        time_span_min (int): Number of minutes, screen lock prevention to last.
        refresh_interval_sec (int): Number of seconds after which
            screen lock prevention is repeated. Default is 30 sec.
    """
    if refresh_interval_sec <= 0:
        refresh_interval_sec = const.DEFAULT_INTERVAL_SEC

    end_time = time.time() + (time_span_min * const.MINUTE)

    while time.time() < end_time:
        prevent_screen_lock()
        time.sleep(refresh_interval_sec)
    release_screen_lock()


_state = _State()
