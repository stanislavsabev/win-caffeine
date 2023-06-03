"""Screen lock implementation."""
import ctypes
import time

from win_caffeine import const

# Define constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


class _State:
    is_on = True
    refresh_interval_sec = 0
    end_time_sec = 0


def reset_duration_time():
    global _state
    _state.end_time_sec = 0
    _state.refresh_interval_sec = 0


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
    duration_min: int,
    refresh_interval_sec: int = const.DEFAULT_INTERVAL_SEC,
    **kwargs,
):
    """Prevent screen lock for amount of time.

    Args:
        duration_min (int): Number of minutes, screen lock prevention to last.
        refresh_interval_sec (int): Number of seconds after which
            screen lock prevention is repeated. Default is 30 sec.
    """
    _state.end_time_sec = time.time() + (duration_min * const.MINUTE)
    _state.refresh_interval_sec = refresh_interval_sec
    progress_callback = kwargs.pop("progress_callback")

    while time.time() < _state.end_time_sec:
        remaining_time = _state.end_time_sec - time.time()
        prevent_screen_lock()

        sleep_interval = 0
        while sleep_interval < _state.refresh_interval_sec:
            time.sleep(1)
            sleep_interval += 1
            remaining_time -= 1
            progress_callback(str(int(remaining_time)))
    release_screen_lock()


_state = _State()
