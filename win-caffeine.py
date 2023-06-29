"""win_coffeine implementation."""
import os
import sys
import logging
import tempfile
from contextlib import contextmanager

from win_caffeine import settings
from win_caffeine import gui

logging.basicConfig(level=logging.DEBUG)


@contextmanager
def single_instance():
    tempdir = tempfile.gettempdir()
    lock_name = f"{settings.APP_NAME}.lock"
    lockfile = os.sep.join([tempdir, lock_name])
    if os.path.isfile(lockfile):
        logging.error("Another instance is already running.")
        sys.exit(1)
    with open(lockfile, 'w') as f: 
        f.write(str(os.getpid()))
    yield
    os.remove(lockfile)


def main():
    # TODO: parse args

    # choose GUI or CLI
    args = []

    with single_instance():
        return gui.run(*args)


if __name__ == "__main__":
    sys.exit(main())
