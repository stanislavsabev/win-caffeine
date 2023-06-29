"""win_coffeine implementation."""
import argparse
import os
import sys
import logging
import tempfile
from contextlib import contextmanager

from win_caffeine import settings
from win_caffeine import screen_lock
from win_caffeine import gui
from win_caffeine import cli

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def stop():
    """Stop application."""
    # get pid
    tempdir = tempfile.gettempdir()
    lock_name = f"{settings.APP_NAME}.lock"
    lockfile = os.sep.join([tempdir, lock_name])
    if os.path.isfile(lockfile):
        with open(lockfile, "r") as f:
            pid = int(f.read())

        # Kill process
        try:
            os.kill(pid, 9)
            logger.info("Process %s terminated.", pid)
        except OSError as e:
            logger.error("Failed to terminate process.", exc_info=e)

        # cleanup
        os.remove(lockfile)
    else:
        logger.info("Could not find running processes to stop.")


@contextmanager
def single_instance():
    """Ensure single app instance."""
    tempdir = tempfile.gettempdir()
    lock_name = f"{settings.APP_NAME}.lock"
    lockfile = os.sep.join([tempdir, lock_name])
    if os.path.isfile(lockfile):
        logger.error("Another instance is already running.")
        sys.exit(0)

    with open(lockfile, "w") as f:
        f.write(str(os.getpid()))

    try:
        yield
    finally:
        os.remove(lockfile)


def main():
    """Main function."""
    usage = f"{settings.APP_NAME} SUBCOMMAND [FLAGS]"
    parser = argparse.ArgumentParser(prog=settings.APP_NAME, usage=usage)

    parser.add_argument(
        "subcommand", type=str, choices=["gui", "cli", "stop"], help="SUBCOMMAND"
    )

    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=settings.DEFAULT_DURATION_MINUTES,
        help="Duration (minutes)",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=settings.DEFAULT_REFRESH_INTERVAL_SECONDS,
        help="Refresh interval (seconds)",
    )

    parser.add_argument(
        "-s",
        "--strategy",
        type=str,
        choices=screen_lock.strategy_names,
        default=screen_lock.strategy_names[settings.DEFAULT_STRATEGY_INDEX],
        help="Suspend strategy",
    )

    args = parser.parse_args()

    if args.subcommand == "stop":
        stop()
        return 0

    with single_instance():
        # choose GUI, CLI or stop
        subcommand = dict(gui=gui.run, cli=cli.run).get(args.subcommand)
        return subcommand(args)


if __name__ == "__main__":
    sys.exit(main())
