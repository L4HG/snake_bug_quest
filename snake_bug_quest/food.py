"""Snake Bug Quest — food spawning."""

import random
from config import GRID_COLS, GRID_ROWS


class Food:
    """Single food pellet on the grid."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.position = (0, 0)

    def spawn(self, occupied):
        """Place food on a random cell that is not in *occupied*."""
        while True:
            pos = (self.rng.randint(0, GRID_COLS - 1),
                   self.rng.randint(0, GRID_ROWS - 1))
            if pos not in occupied:
                break
        self.position = pos
