"""Screen lock implementation."""
import collections
import ctypes
import logging
import time
import typing

from win_caffeine import qt
from win_caffeine import settings

logger = logging.getLogger(__name__)

Strategy = collections.namedtuple("Strategy", ["ndx", "name", "impl"])


class StrategyProtocol(typing.Protocol):
    def suspend_screen_lock(self, **kwargs):
        """Suspends screen lock."""
        ...

    def release_screen_lock_suspend(self):
        """Release screen lock prevention."""
        ...

    def duration_suspend_screen_lock(self, **kwargs):
        """Suspends screen lock for set duration of time.

        Args:
            progress_callback: Callable or None.
        """
        ...


class ThreadExecState:
    # Execution state constants
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def suspend_screen_lock(self, **kwargs):
        """Suspends screen lock."""
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
        """Release screen lock prevention."""
        ctypes.windll.kernel32.SetThreadExecutionState(ThreadExecState.ES_CONTINUOUS)
        model.is_suspend_screen_lock_on = False
        logger.debug(
            "Release SetThreadExecutionState: 0x%x", ThreadExecState.ES_CONTINUOUS
        )

    def duration_suspend_screen_lock(self, **kwargs):
        """Suspends screen lock for set duration of time.

        Args:
            progress_callback: Callable or None.
        """
        model.is_suspend_screen_lock_on = True
        end_time_sec = time.time() + (model.duration_minutes * settings.MINUTE)
        progress_callback = kwargs.get("progress_callback")
        remaining_time = end_time_sec - time.time()

        while time.time() < end_time_sec:
            logger.debug(
                "duration_suspend_screen_lock: remaining_time %d", remaining_time
            )
            self.suspend_screen_lock()
            sleep_interval = 0
            while sleep_interval < model.interval_seconds:
                time.sleep(1)
                sleep_interval += 1
                remaining_time -= 1
                if progress_callback:
                    progress_callback(str(int(remaining_time)))
                if not model.is_suspend_screen_lock_on:
                    return
        self.release_screen_lock_suspend()


class NumLock:
    VK_NUMLOCK = 0x90

    def suspend_screen_lock(self, **kwargs):
        """Suspends screen lock."""
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
        """Release screen lock prevention."""
        model.is_suspend_screen_lock_on = False
        logger.debug("Release NumLock")

    def duration_suspend_screen_lock(self, **kwargs):
        """Suspends screen lock for set duration of time.

        Args:
            progress_callback: Callable or None.
        """
        model.is_suspend_screen_lock_on = True
        end_time_sec = time.time() + (model.duration_minutes * settings.MINUTE)
        progress_callback = kwargs.get("progress_callback")
        remaining_time = end_time_sec - time.time()

        while time.time() < end_time_sec:
            logger.debug(
                "duration_suspend_screen_lock: remaining_time %d", remaining_time
            )
            self.send_key(self.VK_NUMLOCK)
            time.sleep(1)
            self.send_key(self.VK_NUMLOCK)

            sleep_interval = model.interval_seconds
            while sleep_interval > 0:
                time.sleep(1)
                sleep_interval -= 1
                remaining_time -= 1
                if progress_callback:
                    progress_callback(str(int(remaining_time)))
                if not model.is_suspend_screen_lock_on:
                    return
        self.release_screen_lock_suspend()

    def send_key(self, key, up_down_delay=0.1):
        """Sends key via ctypes windll"""
        # key down
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        time.sleep(up_down_delay)
        # key up
        ctypes.windll.user32.keybd_event(key, 0, 0x002, 0)
        logger.debug("Send key 0x%x", key)


strategies = [
    Strategy(0, "NumLock", NumLock()),
    Strategy(1, "ThreadExecState", ThreadExecState()),
]

strategy_names = [strategy.name for strategy in strategies]


class Model:
    """Manages the screen lock state."""

    is_suspend_screen_lock_on = False
    is_duration_checked = False
    duration_minutes = settings.DEFAULT_DURATION_MINUTES
    interval_seconds = settings.DEFAULT_REFRESH_INTERVAL_SECONDS
    strategy: Strategy = strategies[settings.DEFAULT_STRATEGY_INDEX]

    def set_suspended(self, val: bool):
        """Sets suspend state."""
        self.is_suspend_screen_lock_on = val

    def set_strategy(self, ndx: int):
        """Sets strategy for the Screen suspend."""
        self.strategy = strategies[ndx]

    def save_settings(self, usr_settings: qt.QSettings):
        """Saves model settings."""
        usr_settings.beginGroup("ModelSettings")
        usr_settings.setValue("strategy_index", self.strategy.ndx)
        usr_settings.setValue("duration_checked", self.is_duration_checked)
        usr_settings.setValue("duration_minutes", self.duration_minutes)
        usr_settings.setValue("refresh_interval_seconds", self.interval_seconds)
        usr_settings.endGroup()

    def load_settings(self, usr_settings: qt.QSettings):
        """Loads model settings."""
        usr_settings.beginGroup("ModelSettings")
        strategy_ndx = typing.cast(
            int, usr_settings.value("strategy_index", settings.DEFAULT_STRATEGY_INDEX)
        )
        self.set_strategy(strategy_ndx)

        self.is_duration_checked = typing.cast(
            bool, usr_settings.value("duration_checked", False)
        )
        self.duration_minutes = typing.cast(
            int,
            usr_settings.value("duration_minutes", settings.DEFAULT_DURATION_MINUTES),
        )
        self.interval_seconds = typing.cast(
            int,
            usr_settings.value(
                "refresh_interval_seconds", settings.DEFAULT_REFRESH_INTERVAL_SECONDS
            ),
        )
        usr_settings.endGroup()

    def suspend_screen_lock(self, **kwargs):
        """Suspends screen lock."""
        logger.info("--- Suspend screen lock ---\n%s", str(self))
        if self.is_duration_checked:
            self.strategy.impl.duration_suspend_screen_lock(**kwargs)
        else:
            self.strategy.impl.suspend_screen_lock(**kwargs)

    def release_screen_lock_suspend(self):
        """Release screen lock prevention."""
        self.strategy.impl.release_screen_lock_suspend()

    def __str__(self) -> str:
        return ">>> " + "\n>>> ".join(
            [
                f"Duration: {str(self.duration_minutes)} min",
                f"Interval: {str(self.interval_seconds)} sec",
                f"Using duration: {str(self.is_duration_checked)}",
                f"Strategy: {self.strategy.name}",
            ]
        )


model = Model()
