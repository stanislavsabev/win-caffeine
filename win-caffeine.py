"""win_coffeine implementation."""


import sys
import logging

from win_caffeine import gui, settings

logging.basicConfig(level=logging.DEBUG)


def main():
    # TODO: parse args

    # choose GUI or CLI
    args = []

    settings.init()
    return gui.run(*args)


if __name__ == "__main__":
    sys.exit(main())
