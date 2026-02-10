# 🐍🐛 Snake Bug Quest

**Conference booth activity**: use an AI coding assistant (agent mode) to find and fix 5 bugs hidden in a classic Snake game — one by one.

## Setup

```bash
pip install pygame
```

## Run

**Multi-file version** (from `snake_bug_quest/` folder):
```bash
cd snake_bug_quest
python main.py
```

**Single-file version**:
```bash
python snake.py
```

## Controls

| Key | Action |
|-----|--------|
| ↑ ↓ ← → | Move the snake |
| R | Reset progress to Stage 1 & restart |
| ESC | Quit |
| Space | Restart after Game Over (keeps current stage) |

CLI flag: `python main.py --reset` — resets progress without UI.

## How the Activity Works

1. The game starts **broken** — there are **5 sequential bugs** (stages 1–5).
2. The right-side panel shows the current stage, a hint, and debug info.
3. Fix the current bug in the code → the game **auto-detects** the fix and advances to the next stage.
4. Previous bugs must be fixed first — later bugs only manifest after earlier ones are resolved.
5. After all 5 stages → 🎉 **"All Bugs Fixed"** screen.

Participants are encouraged to use an AI agent / assistant inside their IDE to diagnose and fix bugs.

## Progress

- Stored in `progress.json` (auto-created).
- Press **R** or run `--reset` to start over.

## Project Structure (multi-file)

```
snake_bug_quest/
├── main.py          # entry point
├── game.py          # game loop, rendering, speed
├── snake.py         # snake model, movement, growth
├── food.py          # food spawning
├── bug_tracker.py   # auto-detection of bug fixes
├── config.py        # constants & settings
├── progress.py      # progress.json read/write
└── README.md
```

## For Organisers

The 5 stages test progressively deeper understanding:
1. **Input handling** — a direction isn't working
2. **Collision detection** — coordinate system mismatch
3. **State mutation** — wrong growth amount
4. **Spawn logic** — missing constraint
5. **Game balance** — broken speed formula

Each bug is a realistic, common mistake — no artificial "magic" injections.
