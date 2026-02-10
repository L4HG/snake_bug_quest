#!/usr/bin/env python3
"""Snake Bug Quest — entry point.

Usage:
    python main.py            # normal launch
    python main.py --reset    # reset progress to stage 1 and launch
"""

import sys
from progress import reset_progress
from game import Game


def main():
    if "--reset" in sys.argv:
        reset_progress()
        print("[main] Progress reset to stage 1")
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
