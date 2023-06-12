"""Screen lock implementation."""
import collections
import ctypes
import logging
import time
import typing

from win_caffeine import qt
from win_caffeine import settings

logger = logging.getLogger(__name__)

ScreenLock = collections.namedtuple("ScreenLock", ["name", "impl"])


class ScreenLockProtocol(typing.Protocol):
    def suspend_screen_lock(self, **kwargs):
        """Suspends screen lock."""
        ...

    def release_screen_lock_suspend(self):
        """Release screen lock prevention."""
        ...

    def duration_suspend_screen_lock(self, **kwargs):
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

    def suspend_screen_lock(self, **kwargs):
        del kwargs  # unused
        model.is_suspend_screen_lock_on = True
        ctypes.windll.kernel32.SetThreadExecutionState(
            ThreadExecState.ES_CONTINUOUS | ThreadExecState.ES_SYSTEM_REQUIRED
        )
        logger.debug(
            "SetThreadExecutionState: 0x%x",
            ThreadExecState.ES_CONTINUOUS | ThreadExecState.ES_SYSTEM_REQUIRED,
        )
        while model.is_suspend_screen_lock_on:
            time.sleep(1)

    def release_screen_lock_suspend(self):
        ctypes.windll.kernel32.SetThreadExecutionState(ThreadExecState.ES_CONTINUOUS)
        model.is_suspend_screen_lock_on = False
        logger.debug("Release SetThreadExecutionState: 0x%x", ThreadExecState.ES_CONTINUOUS)

    def duration_suspend_screen_lock(self, **kwargs):
        model.is_suspend_screen_lock_on = True
        end_time_sec = time.time() + (model.duration_minutes * settings.MINUTE)
        progress_callback = kwargs.pop("progress_callback")
        remaining_time = end_time_sec - time.time()

        while time.time() < end_time_sec:
            logger.debug("duration_suspend_screen_lock: remaining_time %d", remaining_time)
            self.suspend_screen_lock()
            sleep_interval = 0
            while sleep_interval < model.refresh_interval_seconds:
                time.sleep(1)
                sleep_interval += 1
                remaining_time -= 1
                progress_callback(str(int(remaining_time)))
                if not model.is_suspend_screen_lock_on:
                    return
        self.release_screen_lock_suspend()


class NumLock:
    VK_NUMLOCK = 0x90

    def suspend_screen_lock(self, **kwargs):
        del kwargs  # unused
        model.is_suspend_screen_lock_on = True

        while model.is_suspend_screen_lock_on:
            self.send_key(self.VK_NUMLOCK)
            time.sleep(1)
            self.send_key(self.VK_NUMLOCK)

            sleep_interval = settings.DEFAULT_REFRESH_INTERVAL_SECONDS
            while sleep_interval > 0:
                time.sleep(1)
                sleep_interval -= 1
                if not model.is_suspend_screen_lock_on:
                    logger.debug("suspend_screen_lock return")
                    return
            logger.debug("suspend_screen_lock return is on")

    def release_screen_lock_suspend(self):
        model.is_suspend_screen_lock_on = False
        logger.debug("Release NumLock")

    def duration_suspend_screen_lock(self, **kwargs):
        model.is_suspend_screen_lock_on = True
        end_time_sec = time.time() + (model.duration_minutes * settings.MINUTE)
        progress_callback = kwargs.pop("progress_callback")
        remaining_time = end_time_sec - time.time()

        while time.time() < end_time_sec:
            logger.debug("duration_suspend_screen_lock: remaining_time %d", remaining_time)
            self.send_key(self.VK_NUMLOCK)
            time.sleep(1)
            self.send_key(self.VK_NUMLOCK)

            sleep_interval = model.refresh_interval_seconds
            while sleep_interval > 0:
                time.sleep(1)
                sleep_interval -= 1
                remaining_time -= 1
                progress_callback(str(int(remaining_time)))
                if not model.is_suspend_screen_lock_on:
                    return
        self.release_screen_lock_suspend()

    def send_key(self, key, up_down_delay=0.1):
        # key down
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        time.sleep(up_down_delay)
        # key up
        ctypes.windll.user32.keybd_event(key, 0, 0x002, 0)
        logger.debug("Send key 0x%x", key)


class Model:
    """Manages the screen lock state."""

    strategies = [
        ScreenLock("NumLock", NumLock()),
        ScreenLock("Thread Exec State", ThreadExecState()),
    ]

    is_suspend_screen_lock_on = False
    is_duration_checked = False
    strategy_ndx = settings.DEFAULT_STRATEGY_INDEX
    duration_minutes = settings.DEFAULT_DURATION_MINUTES
    refresh_interval_seconds = settings.DEFAULT_REFRESH_INTERVAL_SECONDS
    impl: ScreenLockProtocol = strategies[settings.DEFAULT_STRATEGY_INDEX].impl

    def set_suspended(self, val: bool):
        """Sets suspend state."""
        self.is_suspend_screen_lock_on = val

    def set_strategy(self, ndx: int):
        """Sets strategy for the Screen suspend."""
        self.impl = self.strategies[ndx].impl
        self.strategy_ndx = ndx

    def save_settings(self, usr_settings: qt.QSettings):
        usr_settings.beginGroup("ModelSettings")
        usr_settings.setValue("strategy_index", self.strategy_ndx)
        usr_settings.setValue("duration_checked", self.is_duration_checked)
        usr_settings.setValue("duration_minutes", self.duration_minutes)
        usr_settings.setValue("refresh_interval_seconds", self.refresh_interval_seconds)
        usr_settings.endGroup()

    def load_settings(self, usr_settings: qt.QSettings):
        usr_settings.beginGroup("ModelSettings")
        self.strategy_ndx = usr_settings.value("strategy_index", settings.DEFAULT_STRATEGY_INDEX)
        self.is_duration_checked = usr_settings.value(
            "duration_checked", False
        )
        self.duration_minutes = usr_settings.value(
            "duration_minutes", settings.DEFAULT_DURATION_MINUTES, int
        )
        self.refresh_interval_seconds = usr_settings.value(
            "refresh_interval_seconds", settings.DEFAULT_REFRESH_INTERVAL_SECONDS, int
        )
        usr_settings.endGroup()

    def suspend_screen_lock(self, **kwargs):
        """Suspends screen lock."""
        if self.is_duration_checked:
            self.impl.duration_suspend_screen_lock(**kwargs)
        else:
            self.impl.suspend_screen_lock(**kwargs)

    def release_screen_lock_suspend(self):
        """Release screen lock prevention."""
        self.impl.release_screen_lock_suspend()


model = Model()
