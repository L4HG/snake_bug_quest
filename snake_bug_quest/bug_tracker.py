"""Snake Bug Quest — fix detectors for stages 1-7."""

from config import (
    DIR_LEFT, GRID_ROWS, SPEED_CAP, TOTAL_STAGES,
)


class BugTracker:
    """Observes game state each tick; returns True when current stage is fixed."""

    def __init__(self, stage: int):
        self.stage = stage
        # per-stage accumulators
        self._left_req = False
        self._left_ttl = 0
        self._prev_score = 0
        self._prev_food = None
        self._eat_snap_len = None
        self._eat_watch = 0
        self._eat_events = 0
        self._good_spawns = 0
        self._speed_ok_ticks = 0
        self._bottom_visits = 0
        self._bottom_ok = 0
        self._clean_body_ticks = 0

    # ── public entry point (called every tick) ─────────────────────
    def tick(self, game) -> bool:
        handler = {
            1: self._s1, 2: self._s2, 3: self._s3,
            4: self._s4, 5: self._s5, 6: self._s6, 7: self._s7,
        }.get(self.stage)
        return handler(game) if handler else False

    # ── notifications from game loop ───────────────────────────────
    def notify_left(self):
        self._left_req = True
        self._left_ttl = 0

    def notify_spawn(self, food_pos, snake_body):
        if self.stage == 4:
            if food_pos in snake_body:
                self._good_spawns = 0
            else:
                self._good_spawns += 1

    # ── stage detectors ────────────────────────────────────────────
    def _s1(self, g) -> bool:
        """LEFT direction accepted at least once."""
        if self._left_req:
            self._left_ttl += 1
            if g.snake.direction == DIR_LEFT:
                return True
            if self._left_ttl > 8:
                self._left_req = False
        return False

    def _s2(self, g) -> bool:
        """Score increases and food repositions after eating."""
        s, f = g.score, g.food.position
        if s > self._prev_score and f != self._prev_food:
            return True
        self._prev_score, self._prev_food = s, f
        return False

    def _s3(self, g) -> bool:
        """After eating, length grows by exactly 1 (not more)."""
        s, ln = g.score, g.snake.length
        if s > self._eat_events:
            self._eat_events = s
            self._eat_snap_len = ln
            self._eat_watch = 0
            return False
        if self._eat_snap_len is not None:
            self._eat_watch += 1
            if self._eat_watch > 8:
                if ln - self._eat_snap_len <= 1:
                    return True
                self._eat_snap_len = None
        return False

    def _s4(self, g) -> bool:
        """Food never overlaps snake body (3 clean spawns in a row)."""
        return self._good_spawns >= 3

    def _s5(self, g) -> bool:
        """Speed stays below cap and doesn't increase every frame."""
        if g.tick_rate > SPEED_CAP:
            self._speed_ok_ticks = 0
            return False
        self._speed_ok_ticks += 1
        return g.score >= 8 and self._speed_ok_ticks > 60

    def _s6(self, g) -> bool:
        """Bottom wall works: snake head never escapes past GRID_ROWS."""
        hy = g.snake.head[1]
        if hy >= GRID_ROWS:
            self._bottom_ok = 0
            return False
        if hy >= GRID_ROWS - 3:
            self._bottom_visits += 1
        self._bottom_ok += 1
        return self._bottom_visits >= 2 and self._bottom_ok >= 40

    def _s7(self, g) -> bool:
        """No duplicate body cells while alive (self-collision works)."""
        body = g.snake.body
        if len(body) != len(set(body)):
            self._clean_body_ticks = 0
            return False
        if g.snake.length > 5:
            self._clean_body_ticks += 1
        return self._clean_body_ticks >= 80
