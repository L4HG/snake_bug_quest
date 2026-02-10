# 🐍🐛 Snake Bug Quest

**Conference booth activity**: use an AI coding assistant (agent mode) to find and fix **7 bugs** hidden in a classic Snake game — one by one.

## Setup

```bash
pip install pygame
```

## Run

**Multi-file** (from `snake_bug_quest/` folder):
```bash
cd snake_bug_quest
python main.py
```

**Single-file**:
```bash
python snake.py
```

## Controls

| Key | Action |
|-----|--------|
| ↑ ↓ ← → | Move the snake |
| R | Reset progress to Stage 1 |
| ESC | Quit |
| Space | Restart after Game Over |

CLI: `python main.py --reset` resets without UI.

## How It Works

1. The game starts **broken** — 7 sequential bugs (stages 1–7).
2. The right panel shows the current stage, a hint, and live debug info.
3. Fix the current bug → the game **auto-detects** and advances.
4. Bugs are ordered so each becomes visible only after previous ones are fixed.
5. Stage 7 cleared → 🎉 **"All Bugs Fixed"** banner.

## Progress

Stored in `progress.json` (auto-created). Press **R** or `--reset` to start over.

## Structure

```
snake_bug_quest/
├── main.py          # entry point
├── game.py          # game loop, rendering
├── snake.py         # snake model, movement
├── food.py          # food spawning
├── bug_tracker.py   # auto-detection of fixes
├── config.py        # constants & key mappings
├── progress.py      # progress.json I/O
└── README.md
```

## For Organisers

The 7 stages test progressively deeper understanding:

| # | Area | Difficulty |
|---|------|-----------|
| 1 | Input handling | ⭐ |
| 2 | Collision logic | ⭐⭐ |
| 3 | Game constants | ⭐ |
| 4 | Function call site | ⭐⭐ |
| 5 | Game-loop formula | ⭐⭐ |
| 6 | Constant mix-up | ⭐⭐⭐ |
| 7 | Temporal logic | ⭐⭐⭐ |

Bugs are spread across multiple files and look like ordinary code — no marker comments, no artificial injection layer.
