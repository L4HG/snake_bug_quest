"""Snake Bug Quest — game state, loop, and rendering."""

import pygame

from config import (
    CELL_SIZE, GRID_COLS, GRID_ROWS,
    GAME_AREA_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT, PANEL_WIDTH,
    BG_COLOR, GRID_COLOR, SNAKE_COLOR, SNAKE_HEAD_COLOR,
    FOOD_COLOR, PANEL_BG, TEXT_COLOR, HIGHLIGHT,
    STAGE_CLR, GAMEOVER_CLR, WIN_CLR,
    INITIAL_SPEED, SPEED_INCREMENT, SPEED_SCORE_INTERVAL, SPEED_CAP,
    RANDOM_SEED, TOTAL_STAGES,
    KEY_TO_NAME, NAME_TO_DIR,
    DIR_LEFT, STAGE_HINTS,
)
from snake import Snake
from food import Food
from bug_tracker import BugTracker
from progress import load_progress, save_progress, reset_progress


class Game:
    """Top-level game controller."""

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

    # ── coordinate helpers (used by renderer + collision) ──────────
    @staticmethod
    def _to_screen(cell):
        """Grid cell → pixel coordinate (top-left corner)."""
        return (cell[0] * CELL_SIZE, cell[1] * CELL_SIZE)

    # ── main loop ──────────────────────────────────────────────────
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

    # ── input ──────────────────────────────────────────────────────
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

    # ── tick ───────────────────────────────────────────────────────
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

    # ── food collision ─────────────────────────────────────────────
    def _check_food(self):
        head_pos = self._to_screen(self.snake.head)
        food_pos = self.food.position
        if head_pos == food_pos:
            self.score += 1
            self.snake.grow()
            self.food.spawn(self.snake.body[:1])
            self.tracker.notify_spawn(self.food.position, self.snake.body)
            print(f"[game] ate food  score={self.score}")

    # ── speed scaling ──────────────────────────────────────────────
    def _update_speed(self):
        self.tick_rate = INITIAL_SPEED + self.frame // 30

    # ════════════════════════════════ rendering ═════════════════════
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
