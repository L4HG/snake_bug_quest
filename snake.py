#!/usr/bin/env python3
"""Snake Bug Quest — single-file edition.

Classic Snake with 7 hidden bugs to find and fix, one at a time.
The game auto-detects each fix and advances to the next stage.

    python snake.py            # launch
    python snake.py --reset    # reset progress & launch
"""

import json, os, random, sys
from datetime import datetime

import pygame

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════

CELL_SIZE = 25
GRID_COLS = 24
GRID_ROWS = 20
PANEL_WIDTH = 260
GAME_AREA_WIDTH = CELL_SIZE * GRID_COLS
WINDOW_WIDTH = GAME_AREA_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_ROWS

BG_COLOR = (15, 15, 26)
GRID_COLOR = (30, 30, 45)
SNAKE_COLOR = (0, 220, 80)
SNAKE_HEAD_COLOR = (0, 255, 120)
FOOD_COLOR = (255, 60, 60)
PANEL_BG = (22, 22, 38)
TEXT_COLOR = (200, 200, 220)
HIGHLIGHT = (80, 200, 255)
STAGE_CLR = (255, 200, 60)
GAMEOVER_CLR = (255, 70, 70)
WIN_CLR = (80, 255, 120)

INITIAL_LENGTH = 3
GROWTH_PER_FOOD = 3
INITIAL_SPEED = 6
SPEED_INCREMENT = 1
SPEED_SCORE_INTERVAL = 5
SPEED_CAP = 14
RANDOM_SEED = 42
TOTAL_STAGES = 7

DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

KEY_TO_NAME = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
}
NAME_TO_DIR = {
    "up": DIR_UP,
    "down": DIR_DOWN,
    "left": DIR_RIGHT,
    "right": DIR_RIGHT,
}

PROGRESS_FILE = "progress.json"

STAGE_HINTS = {
    1: "Hint: Try turning LEFT...",
    2: "Hint: Walk over the food cell",
    3: "Hint: Eat food & watch length",
    4: "Hint: Where does food respawn?",
    5: "Hint: Watch speed over time",
    6: "Hint: Walk along every wall",
    7: "Hint: Can you crash into yourself?",
}

OPPOSITES = {
    DIR_UP: DIR_DOWN,
    DIR_DOWN: DIR_UP,
    DIR_LEFT: DIR_RIGHT,
    DIR_RIGHT: DIR_LEFT,
}


# ═══════════════════════════════════════════════════════════════════
# PROGRESS
# ═══════════════════════════════════════════════════════════════════

def load_progress() -> int:
    if not os.path.exists(PROGRESS_FILE):
        save_progress(1)
        return 1
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        return max(1, min(int(data.get("stage", 1)), TOTAL_STAGES + 1))
    except (json.JSONDecodeError, ValueError):
        save_progress(1)
        return 1


def save_progress(stage: int) -> None:
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"stage": stage, "updated_at": datetime.now().isoformat()}, f, indent=2)


def reset_progress() -> None:
    save_progress(1)


# ═══════════════════════════════════════════════════════════════════
# SNAKE
# ═══════════════════════════════════════════════════════════════════

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

    def set_direction(self, new_dir):
        """Queue direction; reject 180° reversal."""
        if new_dir == OPPOSITES.get(self.direction):
            return
        self._next_dir = new_dir

    def update(self):
        """Advance one step.  Returns True if alive."""
        self.direction = self._next_dir
        dx, dy = self.direction
        hx, hy = self.body[0]
        new_head = (hx + dx, hy + dy)

        nx, ny = new_head
        if nx < 0 or nx >= GRID_COLS or ny < 0 or ny >= GRID_COLS:
            return False

        # Detect self-collision
        if len(self.body) != len(set(self.body)):
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
        """Queue growth after eating."""
        self.pending_growth += GROWTH_PER_FOOD

    @property
    def length(self):
        return len(self.body)


# ═══════════════════════════════════════════════════════════════════
# FOOD
# ═══════════════════════════════════════════════════════════════════

class Food:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.position = (0, 0)

    def spawn(self, occupied):
        """Place food on a random cell not in *occupied*."""
        while True:
            pos = (self.rng.randint(0, GRID_COLS - 1),
                   self.rng.randint(0, GRID_ROWS - 1))
            if pos not in occupied:
                break
        self.position = pos


# ═══════════════════════════════════════════════════════════════════
# BUG TRACKER
# ═══════════════════════════════════════════════════════════════════

class BugTracker:
    def __init__(self, stage: int):
        self.stage = stage
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

    def tick(self, game) -> bool:
        h = {1: self._s1, 2: self._s2, 3: self._s3, 4: self._s4,
             5: self._s5, 6: self._s6, 7: self._s7}.get(self.stage)
        return h(game) if h else False

    def notify_left(self):
        self._left_req = True
        self._left_ttl = 0

    def notify_spawn(self, food_pos, snake_body):
        if self.stage == 4:
            if food_pos in snake_body:
                self._good_spawns = 0
            else:
                self._good_spawns += 1

    def _s1(self, g) -> bool:
        if self._left_req:
            self._left_ttl += 1
            if g.snake.direction == DIR_LEFT:
                return True
            if self._left_ttl > 8:
                self._left_req = False
        return False

    def _s2(self, g) -> bool:
        s, f = g.score, g.food.position
        if s > self._prev_score and f != self._prev_food:
            return True
        self._prev_score, self._prev_food = s, f
        return False

    def _s3(self, g) -> bool:
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
        return self._good_spawns >= 3

    def _s5(self, g) -> bool:
        if g.tick_rate > SPEED_CAP:
            self._speed_ok_ticks = 0
            return False
        self._speed_ok_ticks += 1
        return g.score >= 8 and self._speed_ok_ticks > 60

    def _s6(self, g) -> bool:
        hy = g.snake.head[1]
        if hy >= GRID_ROWS:
            self._bottom_ok = 0
            return False
        if hy >= GRID_ROWS - 3:
            self._bottom_visits += 1
        self._bottom_ok += 1
        return self._bottom_visits >= 2 and self._bottom_ok >= 40

    def _s7(self, g) -> bool:
        body = g.snake.body
        if len(body) != len(set(body)):
            self._clean_body_ticks = 0
            return False
        if g.snake.length > 5:
            self._clean_body_ticks += 1
        return self._clean_body_ticks >= 80


# ═══════════════════════════════════════════════════════════════════
# GAME
# ═══════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Bug Quest 🐍🐛")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 28, bold=True)
        self.stage = load_progress()
        self._new_game()

    def _new_game(self):
        self.snake = Snake()
        self.food = Food(seed=RANDOM_SEED)
        self.food.spawn(self.snake.body)
        self.score = 0
        self.tick_rate = INITIAL_SPEED
        self.alive = True
        self.frame = 0
        self._last_speedup = 0
        self.tracker = BugTracker(self.stage)
        self.all_fixed = self.stage > TOTAL_STAGES

    @staticmethod
    def _to_screen(cell):
        return (cell[0] * CELL_SIZE, cell[1] * CELL_SIZE)

    def run(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    running = self._on_key(ev.key)
            if self.alive and not self.all_fixed:
                self._tick()
            self._draw()
            self.clock.tick(self.tick_rate if self.alive else 15)
        pygame.quit()

    def _on_key(self, key) -> bool:
        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_r:
            reset_progress()
            self.stage = 1
            self._new_game()
            return True
        if not self.alive:
            if key == pygame.K_SPACE:
                self._new_game()
            return True
        if self.all_fixed:
            return True
        name = KEY_TO_NAME.get(key)
        if name:
            direction = NAME_TO_DIR.get(name)
            if direction:
                self.snake.set_direction(direction)
                if name == "left":
                    self.tracker.notify_left()
        return True

    def _tick(self):
        self.frame += 1
        self.alive = self.snake.update()
        if not self.alive:
            return
        self._check_food()
        self._update_speed()
        if self.tracker.tick(self):
            self.stage += 1
            save_progress(self.stage)
            if self.stage > TOTAL_STAGES:
                self.all_fixed = True
                print("[game] 🎉 ALL BUGS FIXED!")
            else:
                self.tracker = BugTracker(self.stage)
                print(f"[game] ▶ stage {self.stage}")
        if self.frame % 40 == 0:
            print(
                f"  dir={self.snake.direction} head={self.snake.head} "
                f"food={self.food.position} len={self.snake.length} "
                f"grow={self.snake.pending_growth} spd={self.tick_rate} "
                f"score={self.score} stg={self.stage}"
            )

    def _check_food(self):
        head_pos = self._to_screen(self.snake.head)
        food_pos = self.food.position
        if head_pos == food_pos:
            self.score += 1
            self.snake.grow()
            self.food.spawn(self.snake.body[:1])
            self.tracker.notify_spawn(self.food.position, self.snake.body)
            print(f"[game] ate food  score={self.score}")

    def _update_speed(self):
        self.tick_rate = INITIAL_SPEED + self.frame // 30

    # ── rendering ──────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_grid()
        self._draw_food()
        self._draw_snake()
        self._draw_panel()
        if not self.alive:
            self._overlay("GAME OVER", GAMEOVER_CLR, "SPACE to retry")
        if self.all_fixed:
            self._overlay("ALL BUGS FIXED ✅", WIN_CLR, "R = reset  |  ESC = exit")
        pygame.display.flip()

    def _draw_grid(self):
        for x in range(0, GAME_AREA_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT + 1, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (GAME_AREA_WIDTH, y))

    def _draw_snake(self):
        for i, cell in enumerate(self.snake.body):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            px, py = self._to_screen(cell)
            rect = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def _draw_food(self):
        px, py = self._to_screen(self.food.position)
        rect = pygame.Rect(px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, FOOD_COLOR, rect, border_radius=6)

    def _draw_panel(self):
        px = GAME_AREA_WIDTH
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, GRID_COLOR, (px, 0), (px, WINDOW_HEIGHT), 2)
        x, y, gap = px + 14, 14, 22

        def lbl(txt, c=TEXT_COLOR):
            nonlocal y
            self.screen.blit(self.font.render(txt, True, c), (x, y))
            y += gap

        lbl("=== BUG QUEST ===", HIGHLIGHT)
        y += 4
        stg = f"Stage: {self.stage}/{TOTAL_STAGES}" if not self.all_fixed else "ALL FIXED ✅"
        lbl(stg, STAGE_CLR)
        y += 4
        lbl(f"Score:   {self.score}")
        lbl(f"Dir:     {self.snake.direction}")
        lbl(f"Head:    {self.snake.head}")
        lbl(f"Food:    {self.food.position}")
        lbl(f"Length:  {self.snake.length}")
        lbl(f"Growth:  {self.snake.pending_growth}")
        lbl(f"Speed:   {self.tick_rate} tps")
        y += 10
        hint = STAGE_HINTS.get(self.stage, "")
        for part in self._wrap(hint, 26):
            lbl(part, STAGE_CLR)
        y += 16
        lbl("Controls:", HIGHLIGHT)
        for t in (" Arrows = move", " R = reset progress",
                   " ESC = quit", " Space = restart"):
            lbl(t)

    def _overlay(self, title, color, subtitle):
        s = pygame.Surface((GAME_AREA_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))
        t = self.big_font.render(title, True, color)
        self.screen.blit(t, t.get_rect(center=(GAME_AREA_WIDTH // 2,
                                                WINDOW_HEIGHT // 2 - 20)))
        t2 = self.font.render(subtitle, True, TEXT_COLOR)
        self.screen.blit(t2, t2.get_rect(center=(GAME_AREA_WIDTH // 2,
                                                  WINDOW_HEIGHT // 2 + 20)))

    @staticmethod
    def _wrap(text, width):
        if not text:
            return []
        words, lines, cur = text.split(), [], ""
        for w in words:
            test = f"{cur} {w}" if cur else w
            if len(test) > width:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_progress()
        print("[main] progress reset")
    Game().run()
