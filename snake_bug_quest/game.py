"""Snake Bug Quest — game state & main loop."""

import pygame

from config import (
    CELL_SIZE, GRID_COLS, GRID_ROWS,
    GAME_AREA_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT, PANEL_WIDTH,
    BG_COLOR, GRID_COLOR, SNAKE_COLOR, SNAKE_HEAD_COLOR,
    FOOD_COLOR, PANEL_BG, TEXT_COLOR, HIGHLIGHT_COLOR,
    STAGE_COLOR, GAMEOVER_COLOR, WIN_COLOR,
    INITIAL_SPEED, SPEED_INCREMENT, SPEED_SCORE_INTERVAL, SPEED_CAP,
    RANDOM_SEED,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    STAGE_HINTS,
)
from snake import Snake
from food import Food
from bug_tracker import BugTracker
from progress import load_progress, save_progress, reset_progress


class Game:
    """Top-level game state and rendering."""

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

    # ============================================================ main loop
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

    # ------------------------------------------------------------ input
    def _handle_key(self, key) -> bool:
        """Returns False to quit."""
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

    # ------------------------------------------------------------ tick
    def _tick(self):
        self.frame_count += 1
        self.alive = self.snake.update()
        if not self.alive:
            return

        self._check_food()
        self._update_speed()

        # Bug tracker check
        fixed = self.tracker.tick(self)
        if fixed:
            self.stage += 1
            save_progress(self.stage)
            if self.stage > 5:
                self.all_fixed = True
                print("[Game] 🎉 ALL BUGS FIXED!")
            else:
                # Re-create tracker for next stage, keep game running
                self.tracker = BugTracker(self.stage)
                print(f"[Game] Advanced to stage {self.stage}")

        # Periodic console log
        if self.frame_count % 30 == 0:
            print(
                f"  dir={self.snake.direction} head={self.snake.head} "
                f"food={self.food.position} len={self.snake.length} "
                f"grow={self.snake.pending_growth} speed={self.tick_rate} "
                f"score={self.score} stage={self.stage}"
            )

    # ------------------------------------------------------------ food
    def _check_food(self):
        """Detect food collision and handle eating.

        Check head vs food position.
        """
        hx, hy = self.snake.head
        fx, fy = self.food.position
        # Compare head with food position
        if (hx * CELL_SIZE, hy * CELL_SIZE) == (fx, fy):
            self.score += 1
            self.snake.grow()
            self.food.spawn(self.snake.body)
            self.tracker.notify_food_spawned(self.food.position, self.snake.body)
            print(f"[Game] Ate food! score={self.score}")

    # ------------------------------------------------------------ speed
    def _update_speed(self):
        """Adjust tick_rate based on score.

        Scale speed with gameplay.
        """
        # Increase speed progressively
        self.tick_rate += SPEED_INCREMENT

    # ============================================================ drawing
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

        label(f"=== BUG QUEST ===", HIGHLIGHT_COLOR)
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
            # Word-wrap hint
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
