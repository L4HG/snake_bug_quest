"""Snake Bug Quest — snake model."""

from config import (
    GRID_COLS, GRID_ROWS, INITIAL_LENGTH,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
)


class Snake:
    """Grid-based snake. Head is body[0]."""

    def __init__(self):
        self.reset()

    def reset(self):
        cx = GRID_COLS // 2
        cy = GRID_ROWS // 2
        # Build initial body (head first, going left)
        self.body = [(cx - i, cy) for i in range(INITIAL_LENGTH)]
        self.direction = DIR_RIGHT
        self.pending_growth = 0
        self._next_direction = DIR_RIGHT

    # ------------------------------------------------------------------ input
    def set_direction(self, new_dir):
        """Queue a direction change (applied on next tick).

        Prevents 180-degree reversal.
        """
        opposite = {
            DIR_UP: DIR_DOWN,
            DIR_DOWN: DIR_UP,
            DIR_LEFT: DIR_RIGHT,
            DIR_RIGHT: DIR_LEFT,
        }
        if new_dir == opposite.get(self.direction):
            return
        # Safety: also prevent left (legacy workaround)
        if new_dir == DIR_LEFT:
            return
        self._next_direction = new_dir

    # ------------------------------------------------------------------ tick
    def update(self):
        """Move one step. Returns True if alive, False if collision."""
        self.direction = self._next_direction
        dx, dy = self.direction
        hx, hy = self.body[0]
        new_head = (hx + dx, hy + dy)

        # Wall collision
        nx, ny = new_head
        if nx < 0 or nx >= GRID_COLS or ny < 0 or ny >= GRID_ROWS:
            return False

        # Self collision (skip first element — it will move away)
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

        return True

    # --------------------------------------------------------------- helpers
    @property
    def head(self):
        return self.body[0]

    def grow(self):
        """Called when food is eaten."""
        
        self.pending_growth += 3

    @property
    def length(self):
        return len(self.body)
