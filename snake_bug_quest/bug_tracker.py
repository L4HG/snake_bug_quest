"""Snake Bug Quest — bug-fix detectors for stages 1-5."""


class BugTracker:
    """Observes game state each tick and decides when a stage is fixed."""

    def __init__(self, stage: int):
        self.stage = stage
        # Stage 1 state
        self._left_requested = False
        self._left_ticks = 0
        # Stage 2 state
        self._prev_score = 0
        self._prev_food = None
        # Stage 3 state
        self._eating_snapshot_len = None
        self._eating_watch_ticks = 0
        self._eating_events = 0
        # Stage 4 state
        self._good_spawns = 0
        # Stage 5 state
        self._last_speed_score = 0
        self._speed_violations = 0
        self._speed_checks = 0

    # ----- call once per tick from game loop -----
    def tick(self, game) -> bool:
        """Check current stage detector. Returns True if stage just fixed."""
        if self.stage == 1:
            return self._check_stage1(game)
        if self.stage == 2:
            return self._check_stage2(game)
        if self.stage == 3:
            return self._check_stage3(game)
        if self.stage == 4:
            return self._check_stage4(game)
        if self.stage == 5:
            return self._check_stage5(game)
        return False

    # ======================================================== Stage 1
    def notify_left_pressed(self):
        """Called when player presses LEFT."""
        self._left_requested = True
        self._left_ticks = 0

    def _check_stage1(self, game) -> bool:
        from config import DIR_LEFT
        if self._left_requested:
            self._left_ticks += 1
            if game.snake.direction == DIR_LEFT:
                print("[BugTracker] Stage 1 FIXED — LEFT turn works!")
                return True
            if self._left_ticks > 5:
                self._left_requested = False  # reset, wait for next attempt
        return False

    # ======================================================== Stage 2
    def _check_stage2(self, game) -> bool:
        score = game.score
        food = game.food.position
        if score > self._prev_score and food != self._prev_food:
            print("[BugTracker] Stage 2 FIXED — food eaten correctly!")
            return True
        self._prev_score = score
        self._prev_food = food
        return False

    # ======================================================== Stage 3
    def _check_stage3(self, game) -> bool:
        score = game.score
        slen = game.snake.length

        # Detect eating event
        if score > self._eating_events:
            self._eating_events = score
            self._eating_snapshot_len = slen  # length right after eating (head moved, food consumed)
            self._eating_watch_ticks = 0
            return False

        # Watch growth after eating
        if self._eating_snapshot_len is not None:
            self._eating_watch_ticks += 1
            growth = slen - self._eating_snapshot_len
            if self._eating_watch_ticks > 6:
                # After several ticks growth should be exactly +1 from snapshot
                # (snapshot taken right when eat happens, body already has new head
                #  but pending_growth not yet consumed; so net +1 expected after drain)
                if growth <= 1:
                    print("[BugTracker] Stage 3 FIXED — growth is exactly +1!")
                    return True
                else:
                    # Still buggy, reset
                    self._eating_snapshot_len = None
        return False

    # ======================================================== Stage 4
    def notify_food_spawned(self, food_pos, snake_body):
        """Called right after food.spawn()."""
        if self.stage != 4:
            return
        if food_pos in snake_body:
            self._good_spawns = 0  # reset streak
        else:
            self._good_spawns += 1

    def _check_stage4(self, game) -> bool:
        if self._good_spawns >= 3:
            print("[BugTracker] Stage 4 FIXED — food avoids snake body!")
            return True
        return False

    # ======================================================== Stage 5
    def notify_speed_change(self, new_speed, current_score):
        """Called whenever tick_rate changes."""
        if self.stage != 5:
            return
        self._speed_checks += 1
        score_delta = current_score - self._last_speed_score
        self._last_speed_score = current_score

    def _check_stage5(self, game) -> bool:
        from config import SPEED_CAP
        # Check: speed should never exceed cap
        if game.tick_rate > SPEED_CAP:
            self._speed_violations += 1
            return False
        # Need at least 6 score points to validate
        if game.score >= 6 and game.tick_rate <= SPEED_CAP:
            print("[BugTracker] Stage 5 FIXED — speed scales properly!")
            return True
        return False
