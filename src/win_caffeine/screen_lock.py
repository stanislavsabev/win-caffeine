"""Screen lock implementation."""
import collections
import ctypes
import time
import typing

from win_caffeine import settings


ScreenLock = collections.namedtuple("ScreenLock", ["name", "impl"])


class ScreenLockProtocol(typing.Protocol):
    def suspend_screen_lock(self):
        """Suspends screen lock."""
        ...

    def release_screen_lock_suspend(self):
        """Release screen lock prevention."""
        ...

    def duration_suspend_screen_lock(
        self,
        duration_min: int,
        refresh_interval_sec: int,
        **kwargs,
    ):
        """Suspends screen lock for set duration of time.

        Args:
            duration_min (int): Number of minutes, screen lock prevention to last.
            refresh_interval_sec (int): Number of seconds after which
                screen lock prevention is repeated. Default is 30 sec.
        """
        ...


class ThreadExecState:
    # Execution state constants
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def suspend_screen_lock(self):
        ctypes.windll.kernel32.SetThreadExecutionState(
            ThreadExecState.ES_CONTINUOUS | ThreadExecState.ES_SYSTEM_REQUIRED
        )

    def release_screen_lock_suspend(self):
        ctypes.windll.kernel32.SetThreadExecutionState(ThreadExecState.ES_CONTINUOUS)

    def duration_suspend_screen_lock(
        self,
        duration_min: int,
        refresh_interval_sec: int = settings.DEFAULT_INTERVAL_SEC,
        **kwargs,
    ):
        _state.end_time_sec = time.time() + (duration_min * settings.MINUTE)
        _state.refresh_interval_sec = refresh_interval_sec
        progress_callback = kwargs.pop("progress_callback")

        while time.time() < _state.end_time_sec:
            remaining_time = _state.end_time_sec - time.time()
            self.suspend_screen_lock()

            sleep_interval = 0
            while sleep_interval < _state.refresh_interval_sec:
                time.sleep(1)
                sleep_interval += 1
                remaining_time -= 1
                progress_callback(str(int(remaining_time)))
        self.release_screen_lock_suspend()


class NumLock:
    def suspend_screen_lock(self):
        pass

    def release_screen_lock_suspend(self):
        pass

    def duration_suspend_screen_lock(
        self,
        duration_min: int,
        refresh_interval_sec: int = settings.DEFAULT_INTERVAL_SEC,
        **kwargs,
    ):
        _state.end_time_sec = time.time() + (duration_min * settings.MINUTE)
        _state.refresh_interval_sec = refresh_interval_sec
        progress_callback = kwargs.pop("progress_callback")


def suspend_screen_lock():
    """Suspends screen lock."""
    _state.impl.suspend_screen_lock()


def release_screen_lock_suspend():
    """Release screen lock prevention."""
    _state.impl.release_screen_lock_suspend()


def duration_suspend_screen_lock(
    duration_min: int,
    refresh_interval_sec: int = settings.DEFAULT_INTERVAL_SEC,
    **kwargs,
):
    """Suspends screen lock for set duration of time.

    Args:
        duration_min (int): Number of minutes, screen lock prevention to last.
        refresh_interval_sec (int): Number of seconds after which
            screen lock prevention is repeated. Default is 30 sec.
    """
    _state.impl.duration_suspend_screen_lock(duration_min, refresh_interval_sec, **kwargs)


def reset_duration_time():
    """Resets state end time and refresh interval."""
    _state.end_time_sec = 0
    _state.refresh_interval_sec = 0


def set_strategy(ndx: int):
    """Sets strategy for the Screen suspend."""
    _state.impl = strategies[ndx].impl


strategies = [
    ScreenLock("NumLock", NumLock()),
    ScreenLock("Thread Exec State", ThreadExecState()),
]


class _State:
    """Manages the screen lock state."""

    impl: ScreenLockProtocol = strategies[0].impl
    refresh_interval_sec = 0
    end_time_sec = 0


_state = _State()
