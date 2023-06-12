"""Screen lock implementation."""
import collections
import ctypes
import logging
import time
import typing

from win_caffeine import settings

logger = logging.getLogger(__name__)

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
        _state.is_suspend_screen_lock_on = True
        ctypes.windll.kernel32.SetThreadExecutionState(
            ThreadExecState.ES_CONTINUOUS | ThreadExecState.ES_SYSTEM_REQUIRED
        )
        logger.debug(
            "SetThreadExecutionState: 0x%x",
            ThreadExecState.ES_CONTINUOUS | ThreadExecState.ES_SYSTEM_REQUIRED,
        )
        while _state.is_suspend_screen_lock_on:
            time.sleep(1)

    def release_screen_lock_suspend(self):
        ctypes.windll.kernel32.SetThreadExecutionState(ThreadExecState.ES_CONTINUOUS)
        _state.is_suspend_screen_lock_on = False
        logger.debug(
            "Release SetThreadExecutionState: 0x%x", ThreadExecState.ES_CONTINUOUS
        )

    def duration_suspend_screen_lock(
        self,
        duration_min: int,
        refresh_interval_sec: int = settings.DEFAULT_REFRESH_INTERVAL_SECONDS,
        **kwargs,
    ):
        _state.is_suspend_screen_lock_on = True
        _state.end_time_sec = time.time() + (duration_min * settings.MINUTE)
        _state.refresh_interval_sec = refresh_interval_sec
        progress_callback = kwargs.pop("progress_callback")

        while time.time() < _state.end_time_sec:
            remaining_time = _state.end_time_sec - time.time()
            logger.debug(
                "duration_suspend_screen_lock: remaining_time %d", remaining_time
            )
            self.suspend_screen_lock()
            sleep_interval = 0
            while sleep_interval < _state.refresh_interval_sec:
                time.sleep(1)
                sleep_interval += 1
                remaining_time -= 1
                progress_callback(str(int(remaining_time)))
                if not _state.is_suspend_screen_lock_on:
                    return
        self.release_screen_lock_suspend()


class NumLock:
    VK_NUMLOCK = 0x90

    def suspend_screen_lock(self):
        _state.is_suspend_screen_lock_on = True

        while _state.is_suspend_screen_lock_on:
            self.send_key(self.VK_NUMLOCK)
            time.sleep(1)
            self.send_key(self.VK_NUMLOCK)

            sleep_interval = settings.DEFAULT_REFRESH_INTERVAL_SECONDS
            while sleep_interval > 0:
                time.sleep(1)
                sleep_interval -= 1
                if not _state.is_suspend_screen_lock_on:
                    logger.debug("suspend_screen_lock return")
                    return
                logger.debug("suspend_screen_lock return is on")

    def release_screen_lock_suspend(self):
        _state.is_suspend_screen_lock_on = False
        logger.debug("Release NumLock")

    def duration_suspend_screen_lock(
        self,
        duration_min: int,
        refresh_interval_sec: int = settings.DEFAULT_REFRESH_INTERVAL_SECONDS,
        **kwargs,
    ):
        _state.is_suspend_screen_lock_on = True
        _state.end_time_sec = time.time() + (duration_min * settings.MINUTE)
        _state.refresh_interval_sec = refresh_interval_sec
        progress_callback = kwargs.pop("progress_callback")
        while time.time() < _state.end_time_sec:
            remaining_time = _state.end_time_sec - time.time()
            logger.debug(
                "duration_suspend_screen_lock: remaining_time %d", remaining_time
            )
            self.send_key(self.VK_NUMLOCK)
            time.sleep(1)
            self.send_key(self.VK_NUMLOCK)

            sleep_interval = _state.refresh_interval_sec
            while sleep_interval > 0:
                time.sleep(1)
                sleep_interval -= 1
                remaining_time -= 1
                progress_callback(str(int(remaining_time)))
                if not _state.is_suspend_screen_lock_on:
                    return
        self.release_screen_lock_suspend()

    def send_key(self, key, up_down_delay=0.1):
        # key down
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        time.sleep(up_down_delay)
        # key up
        ctypes.windll.user32.keybd_event(key, 0, 0x002, 0)
        logger.debug("Send key 0x%x", key)


def suspend_screen_lock(**kwargs):
    """Suspends screen lock."""
    del kwargs  # unused
    _state.impl.suspend_screen_lock()


def release_screen_lock_suspend():
    """Release screen lock prevention."""
    _state.impl.release_screen_lock_suspend()


def duration_suspend_screen_lock(
    duration_min: int,
    refresh_interval_sec: int = settings.DEFAULT_REFRESH_INTERVAL_SECONDS,
    **kwargs,
):
    """Suspends screen lock for set duration of time.

    Args:
        duration_min (int): Number of minutes, screen lock prevention to last.
        refresh_interval_sec (int): Number of seconds after which
            screen lock prevention is repeated. Default is 30 sec.
    """
    _state.impl.duration_suspend_screen_lock(
        duration_min, refresh_interval_sec, **kwargs
    )


def set_strategy(ndx: int):
    """Sets strategy for the Screen suspend."""
    _state.impl = strategies[ndx].impl
    _state.strategy_ndx = ndx


def get_strategy() -> int:
    """Gets strategy index for the Screen suspend."""
    return _state.strategy_ndx


def get_suspended():
    """Gets suspend state."""
    return _state.is_suspend_screen_lock_on


def set_suspended(val: bool):
    """Sets suspend state."""
    _state.is_suspend_screen_lock_on = val


strategies = [
    ScreenLock("NumLock", NumLock()),
    ScreenLock("Thread Exec State", ThreadExecState()),
]


class _State:
    """Manages the screen lock state."""

    is_suspend_screen_lock_on = False
    strategy_ndx = 0
    impl: ScreenLockProtocol = strategies[0].impl
    refresh_interval_sec = 0
    end_time_sec = 0


_state = _State()
