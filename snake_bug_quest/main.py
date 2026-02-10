#!/usr/bin/env python3
"""Snake Bug Quest — entry point.

    python main.py            # launch
    python main.py --reset    # reset progress & launch
"""

import sys
from progress import reset_progress
from game import Game

if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_progress()
        print("[main] progress reset")
    Game().run()
