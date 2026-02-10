"""Snake Bug Quest — configuration constants."""

# --- Window / Grid ---
CELL_SIZE = 25
GRID_COLS = 24
GRID_ROWS = 20
PANEL_WIDTH = 260
WINDOW_WIDTH = CELL_SIZE * GRID_COLS + PANEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_ROWS
GAME_AREA_WIDTH = CELL_SIZE * GRID_COLS

# --- Colours (R, G, B) ---
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

# --- Gameplay ---
INITIAL_SPEED = 8          # ticks per second at start
SPEED_INCREMENT = 1        # +FPS per speed-up step
SPEED_SCORE_INTERVAL = 3   # every N score points → speed up
SPEED_CAP = 18             # max ticks per second
RANDOM_SEED = 42
INITIAL_LENGTH = 3

# --- Progress file ---
PROGRESS_FILE = "progress.json"

# --- Directions (dx, dy in grid cells) ---
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# --- Stage hints shown on the panel ---
STAGE_HINTS = {
    1: "Hint: Try turning LEFT...",
    2: "Hint: Walk over the food cell",
    3: "Hint: Eat food & watch length",
    4: "Hint: Where does food respawn?",
    5: "Hint: Watch speed after scoring",
}
