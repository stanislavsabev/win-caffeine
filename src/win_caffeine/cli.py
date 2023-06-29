"""CLI app implementation."""
import logging

from win_caffeine import screen_lock, utils

logger = logging.getLogger(__name__)


def progress_callback(msg: str):
    """CLI progress callback."""
    msg = utils.get_time_hh_mm_ss(int(msg))
    logger.info("Remaining time: %s", msg)


def run(args) -> int:
    """Run CLI app."""
    model = screen_lock.model
    model.duration_minutes = args.duration
    model.interval_seconds = args.interval
    model.is_duration_checked = args.duration > 0 and args.interval > 0
    model.is_suspend_screen_lock_on = False

    for ndx, strat in enumerate(screen_lock.strategies):
        if strat.name == args.strategy:
            model.set_strategy(ndx)
            break

    screen_lock.model.suspend_screen_lock(progress_callback=progress_callback)
    logger.debug("Exiting cli.run.")
    return 0
