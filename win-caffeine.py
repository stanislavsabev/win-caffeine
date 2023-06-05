"""win_coffeine implementation."""


import sys

from win_caffeine import gui


def main():
    # TODO: parse args

    # choose GUI or CLI
    args = []
    return gui.run(*args)


if __name__ == "__main__":
    sys.exit(main())
