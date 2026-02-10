"""Snake Bug Quest — food spawning."""

import random

from config import GRID_COLS, GRID_ROWS


class Food:
    """Single food pellet on the grid."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.position = (0, 0)

    def spawn(self, snake_body: list[tuple[int, int]]):
        """Pick a random free cell for food."""
        x = self.rng.randint(0, GRID_COLS - 1)
        y = self.rng.randint(0, GRID_ROWS - 1)
        
        self.position = (x, y)
