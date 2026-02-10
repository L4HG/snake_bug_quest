"""Snake Bug Quest — progress persistence."""

import json, os
from datetime import datetime
from config import PROGRESS_FILE, TOTAL_STAGES


def load_progress() -> int:
    """Return current stage (1..TOTAL_STAGES). Creates file if absent."""
    if not os.path.exists(PROGRESS_FILE):
        save_progress(1)
        return 1
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        stage = int(data.get("stage", 1))
        return max(1, min(stage, TOTAL_STAGES + 1))
    except (json.JSONDecodeError, ValueError):
        save_progress(1)
        return 1


def save_progress(stage: int) -> None:
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"stage": stage, "updated_at": datetime.now().isoformat()}, f, indent=2)


def reset_progress() -> None:
    save_progress(1)
