#!/usr/bin/env python3
"""Snake Bug Quest — single-file version.

A classic Snake game with 5 intentional bugs (stages 1-5).
Fix them one by one — the game auto-detects each fix!

Usage:
    python snake.py            # normal launch
    python snake.py --reset    # reset progress to stage 1
"""

import json
import os
import random
import sys
from datetime import datetime

import pygame

# ====================================================================
# CONFIG
# ====================================================================

CELL_SIZE = 25
GRID_COLS = 24
GRID_ROWS = 20
PANEL_WIDTH = 260
WINDOW_WIDTH = CELL_SIZE * GRID_COLS + PANEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_ROWS
GAME_AREA_WIDTH = CELL_SIZE * GRID_COLS

BG_COLOR = (15, 15, 26)
GRID_COLOR = (30, 30, 45)
SNAKE_COLOR = (0, 220, 80)
SNAKE_HEAD_COLOR = (0, 255, 120)
FOOD_COLOR = (255, 60, 60)
PANEL_BG = (22, 22, 38)
TEXT_COLOR = (200, 200, 220)
HIGHLIGHT_COLOR = (80, 200, 255)
STAGE_COLOR = (255, 200, 60)
GAMEOVER_COLOR = (255, 70, 70)
WIN_COLOR = (80, 255, 120)

INITIAL_SPEED = 8
SPEED_INCREMENT = 1
SPEED_SCORE_INTERVAL = 3
SPEED_CAP = 18
RANDOM_SEED = 42
INITIAL_LENGTH = 3

PROGRESS_FILE = "progress.json"

DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

STAGE_HINTS = {
    1: "Hint: Try turning LEFT...",
    2: "Hint: Walk over the food cell",
    3: "Hint: Eat food & watch length",
    4: "Hint: Where does food respawn?",
    5: "Hint: Watch speed after scoring",
}


# ====================================================================
# PROGRESS
# ====================================================================

def load_progress() -> int:
    if not os.path.exists(PROGRESS_FILE):
        save_progress(1)
        return 1
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        stage = int(data.get("stage", 1))
        if stage < 1 or stage > 6:
            stage = 1
        return stage
    except (json.JSONDecodeError, ValueError, KeyError):
        save_progress(1)
        return 1


def save_progress(stage: int) -> None:
    data = {"stage": stage, "updated_at": datetime.now().isoformat()}
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def reset_progress() -> None:
    save_progress(1)


# ====================================================================
# SNAKE
# ====================================================================

class Snake:
    """Grid-based snake. Head is body[0]."""

    def __init__(self):
        self.reset()

    def reset(self):
        cx = GRID_COLS // 2
        cy = GRID_ROWS // 2
        self.body = [(cx - i, cy) for i in range(INITIAL_LENGTH)]
        self.direction = DIR_RIGHT
        self.pending_growth = 0
        self._next_direction = DIR_RIGHT

    def set_direction(self, new_dir):
        """Queue direction change. Prevents 180-degree reversal."""
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

    def update(self):
        """Move one step. Returns True if alive."""
        self.direction = self._next_direction
        dx, dy = self.direction
        hx, hy = self.body[0]
        new_head = (hx + dx, hy + dy)

        nx, ny = new_head
        if nx < 0 or nx >= GRID_COLS or ny < 0 or ny >= GRID_ROWS:
            return False
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()
        return True

    @property
    def head(self):
        return self.body[0]

    def grow(self):
        """Called when food is eaten."""
        
        self.pending_growth += 3

    @property
    def length(self):
        return len(self.body)


# ====================================================================
# FOOD
# ====================================================================

class Food:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.position = (0, 0)

    def spawn(self, snake_body: list[tuple[int, int]]):
        """Pick a random cell for food.

        """
        x = self.rng.randint(0, GRID_COLS - 1)
        y = self.rng.randint(0, GRID_ROWS - 1)
        self.position = (x, y)


# ====================================================================
# BUG TRACKER
# ====================================================================

class BugTracker:
    """Observes game state each tick and decides when a stage is fixed."""

    def __init__(self, stage: int):
        self.stage = stage
        self._left_requested = False
        self._left_ticks = 0
        self._prev_score = 0
        self._prev_food = None
        self._eating_snapshot_len = None
        self._eating_watch_ticks = 0
        self._eating_events = 0
        self._good_spawns = 0
        self._last_speed_score = 0
        self._speed_violations = 0
        self._speed_checks = 0

    def tick(self, game) -> bool:
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

    # -- Stage 1 --
    def notify_left_pressed(self):
        self._left_requested = True
        self._left_ticks = 0

    def _check_stage1(self, game) -> bool:
        if self._left_requested:
            self._left_ticks += 1
            if game.snake.direction == DIR_LEFT:
                print("[BugTracker] Stage 1 FIXED — LEFT turn works!")
                return True
            if self._left_ticks > 5:
                self._left_requested = False
        return False

    # -- Stage 2 --
    def _check_stage2(self, game) -> bool:
        score = game.score
        food = game.food.position
        if score > self._prev_score and food != self._prev_food:
            print("[BugTracker] Stage 2 FIXED — food eaten correctly!")
            return True
        self._prev_score = score
        self._prev_food = food
        return False

    # -- Stage 3 --
    def _check_stage3(self, game) -> bool:
        score = game.score
        slen = game.snake.length
        if score > self._eating_events:
            self._eating_events = score
            self._eating_snapshot_len = slen
            self._eating_watch_ticks = 0
            return False
        if self._eating_snapshot_len is not None:
            self._eating_watch_ticks += 1
            growth = slen - self._eating_snapshot_len
            if self._eating_watch_ticks > 6:
                if growth <= 1:
                    print("[BugTracker] Stage 3 FIXED — growth is exactly +1!")
                    return True
                else:
                    self._eating_snapshot_len = None
        return False

    # -- Stage 4 --
    def notify_food_spawned(self, food_pos, snake_body):
        if self.stage != 4:
            return
        if food_pos in snake_body:
            self._good_spawns = 0
        else:
            self._good_spawns += 1

    def _check_stage4(self, game) -> bool:
        if self._good_spawns >= 3:
            print("[BugTracker] Stage 4 FIXED — food avoids snake body!")
            return True
        return False

    # -- Stage 5 --
    def notify_speed_change(self, new_speed, current_score):
        if self.stage != 5:
            return
        self._speed_checks += 1
        self._last_speed_score = current_score

    def _check_stage5(self, game) -> bool:
        if game.tick_rate > SPEED_CAP:
            self._speed_violations += 1
            return False
        if game.score >= 6 and game.tick_rate <= SPEED_CAP:
            print("[BugTracker] Stage 5 FIXED — speed scales properly!")
            return True
        return False


# ====================================================================
# GAME
# ====================================================================

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Bug Quest 🐍🐛")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 28, bold=True)
        self.stage = load_progress()
        self._init_game_state()

    def _init_game_state(self):
        self.snake = Snake()
        self.food = Food(seed=RANDOM_SEED)
        self.food.spawn(self.snake.body)
        self.score = 0
        self.tick_rate = INITIAL_SPEED
        self.alive = True
        self.frame_count = 0
        self._last_speed_up_score = 0
        self.tracker = BugTracker(self.stage)
        self.all_fixed = self.stage > 5

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event.key)
                    if not running:
                        break

            if self.alive and not self.all_fixed:
                self._tick()

            self._draw()
            self.clock.tick(self.tick_rate if self.alive else 15)
        pygame.quit()

    def _handle_key(self, key) -> bool:
        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_r:
            reset_progress()
            self.stage = 1
            self._init_game_state()
            print("[Game] Progress reset to stage 1")
            return True
        if not self.alive:
            if key == pygame.K_SPACE:
                self._init_game_state()
            return True
        if self.all_fixed:
            return True

        direction_map = {
            pygame.K_UP: DIR_UP,
            pygame.K_DOWN: DIR_DOWN,
            pygame.K_LEFT: DIR_LEFT,
            pygame.K_RIGHT: DIR_RIGHT,
        }
        if key in direction_map:
            new_dir = direction_map[key]
            self.snake.set_direction(new_dir)
            if new_dir == DIR_LEFT:
                self.tracker.notify_left_pressed()
        return True

    def _tick(self):
        self.frame_count += 1
        self.alive = self.snake.update()
        if not self.alive:
            return

        self._check_food()
        self._update_speed()

        fixed = self.tracker.tick(self)
        if fixed:
            self.stage += 1
            save_progress(self.stage)
            if self.stage > 5:
                self.all_fixed = True
                print("[Game] 🎉 ALL BUGS FIXED!")
            else:
                self.tracker = BugTracker(self.stage)
                print(f"[Game] Advanced to stage {self.stage}")

        if self.frame_count % 30 == 0:
            print(
                f"  dir={self.snake.direction} head={self.snake.head} "
                f"food={self.food.position} len={self.snake.length} "
                f"grow={self.snake.pending_growth} speed={self.tick_rate} "
                f"score={self.score} stage={self.stage}"
            )

    def _check_food(self):
        """Detect food collision.

        Check head vs food.
        """
        hx, hy = self.snake.head
        fx, fy = self.food.position
        if (hx * CELL_SIZE, hy * CELL_SIZE) == (fx, fy):
            self.score += 1
            self.snake.grow()
            self.food.spawn(self.snake.body)
            self.tracker.notify_food_spawned(self.food.position, self.snake.body)
            print(f"[Game] Ate food! score={self.score}")

    def _update_speed(self):
        """Adjust tick_rate.

        Scale speed with gameplay.
        """
        self.tick_rate += SPEED_INCREMENT

    # ---- drawing ----
    def _draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_grid()
        self._draw_food()
        self._draw_snake()
        self._draw_panel()
        if not self.alive:
            self._draw_gameover()
        if self.all_fixed:
            self._draw_win()
        pygame.display.flip()

    def _draw_grid(self):
        for x in range(0, GAME_AREA_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT + 1, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (GAME_AREA_WIDTH, y))

    def _draw_snake(self):
        for i, (gx, gy) in enumerate(self.snake.body):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            rect = pygame.Rect(gx * CELL_SIZE + 1, gy * CELL_SIZE + 1,
                               CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def _draw_food(self):
        fx, fy = self.food.position
        rect = pygame.Rect(fx * CELL_SIZE + 2, fy * CELL_SIZE + 2,
                           CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, FOOD_COLOR, rect, border_radius=6)

    def _draw_panel(self):
        panel_x = GAME_AREA_WIDTH
        pygame.draw.rect(self.screen, PANEL_BG,
                         (panel_x, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, GRID_COLOR,
                         (panel_x, 0), (panel_x, WINDOW_HEIGHT), 2)
        x = panel_x + 14
        y = 14
        gap = 22

        def label(txt, color=TEXT_COLOR):
            nonlocal y
            surf = self.font.render(txt, True, color)
            self.screen.blit(surf, (x, y))
            y += gap

        label("=== BUG QUEST ===", HIGHLIGHT_COLOR)
        y += 4
        stage_text = f"Stage: {self.stage}/5" if self.stage <= 5 else "ALL FIXED ✅"
        label(stage_text, STAGE_COLOR)
        y += 4
        label(f"Score:   {self.score}")
        label(f"Dir:     {self.snake.direction}")
        label(f"Head:    {self.snake.head}")
        label(f"Food:    {self.food.position}")
        label(f"Length:  {self.snake.length}")
        label(f"Growth:  {self.snake.pending_growth}")
        label(f"Speed:   {self.tick_rate} tps")
        y += 10
        hint = STAGE_HINTS.get(self.stage, "")
        if hint:
            words = hint.split()
            line = ""
            for w in words:
                test = line + " " + w if line else w
                if len(test) > 26:
                    label(line, STAGE_COLOR)
                    line = w
                else:
                    line = test
            if line:
                label(line, STAGE_COLOR)
        y += 16
        label("Controls:", HIGHLIGHT_COLOR)
        label(" Arrows = move")
        label(" R = reset progress")
        label(" ESC = quit")
        label(" Space = restart")
        label("   (after game over)")

    def _draw_gameover(self):
        overlay = pygame.Surface((GAME_AREA_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        txt = self.big_font.render("GAME OVER", True, GAMEOVER_COLOR)
        r = txt.get_rect(center=(GAME_AREA_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(txt, r)
        sub = self.font.render("Press SPACE to retry", True, TEXT_COLOR)
        r2 = sub.get_rect(center=(GAME_AREA_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(sub, r2)

    def _draw_win(self):
        overlay = pygame.Surface((GAME_AREA_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        txt = self.big_font.render("ALL BUGS FIXED ✅", True, WIN_COLOR)
        r = txt.get_rect(center=(GAME_AREA_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(txt, r)
        sub = self.font.render("R = reset  |  ESC = exit", True, TEXT_COLOR)
        r2 = sub.get_rect(center=(GAME_AREA_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(sub, r2)


# ====================================================================
# ENTRY POINT
# ====================================================================

def main():
    if "--reset" in sys.argv:
        reset_progress()
        print("[main] Progress reset to stage 1")
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
