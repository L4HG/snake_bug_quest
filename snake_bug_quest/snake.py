"""Snake Bug Quest — snake model."""

from config import (
    GRID_COLS, GRID_ROWS, INITIAL_LENGTH, GROWTH_PER_FOOD,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
)

OPPOSITES = {
    DIR_UP: DIR_DOWN,
    DIR_DOWN: DIR_UP,
    DIR_LEFT: DIR_RIGHT,
    DIR_RIGHT: DIR_LEFT,
}


class Snake:
    """Grid-based snake.  body[0] is the head."""

    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        self.body = [(cx - i, cy) for i in range(INITIAL_LENGTH)]
        self.direction = DIR_RIGHT
        self.pending_growth = 0
        self._next_dir = DIR_RIGHT

    # ── direction ──────────────────────────────────────────────────
    def set_direction(self, new_dir):
        """Queue direction; rejects 180° reversal."""
        if new_dir == OPPOSITES.get(self.direction):
            return
        self._next_dir = new_dir

    # ── tick ───────────────────────────────────────────────────────
    def update(self):
        """Advance one step.  Returns True if alive."""
        self.direction = self._next_dir
        dx, dy = self.direction
        hx, hy = self.body[0]
        new_head = (hx + dx, hy + dy)

        # Boundary check
        nx, ny = new_head
        if nx < 0 or nx >= GRID_COLS or ny < 0 or ny >= GRID_COLS:
            return False

        # Self-collision: detect any duplicate cell in the body
        if len(self.body) != len(set(self.body)):
            return False

        self.body.insert(0, new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

        return True

    # ── helpers ────────────────────────────────────────────────────
    @property
    def head(self):
        return self.body[0]

    def grow(self):
        """Queue growth after eating."""
        self.pending_growth += GROWTH_PER_FOOD

    @property
    def length(self):
        return len(self.body)
