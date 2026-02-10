"""Snake Bug Quest — configuration."""

import pygame

# ── Window / Grid ──────────────────────────────────────────────────
CELL_SIZE = 25
GRID_COLS = 24
GRID_ROWS = 20
PANEL_WIDTH = 260
GAME_AREA_WIDTH = CELL_SIZE * GRID_COLS
WINDOW_WIDTH = GAME_AREA_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_ROWS

# ── Colours ────────────────────────────────────────────────────────
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

# ── Gameplay ───────────────────────────────────────────────────────
INITIAL_LENGTH = 3
GROWTH_PER_FOOD = 3
INITIAL_SPEED = 6
SPEED_INCREMENT = 1
SPEED_SCORE_INTERVAL = 5
SPEED_CAP = 14
RANDOM_SEED = 42
TOTAL_STAGES = 7

# ── Directions ─────────────────────────────────────────────────────
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# ── Input mapping (key → name → vector) ───────────────────────────
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

# ── Progress ───────────────────────────────────────────────────────
PROGRESS_FILE = "progress.json"

# ── Stage hints ────────────────────────────────────────────────────
STAGE_HINTS = {
    1: "Hint: Try turning LEFT...",
    2: "Hint: Walk over the food cell",
    3: "Hint: Eat food & watch length",
    4: "Hint: Where does food respawn?",
    5: "Hint: Walk along every wall",
    6: "Hint: Can you crash into yourself?",
    7: "Hint: Watch speed over time",
}
