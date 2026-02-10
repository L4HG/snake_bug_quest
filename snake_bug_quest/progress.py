"""Snake Bug Quest — progress persistence (progress.json)."""

import json
import os
from datetime import datetime

from config import PROGRESS_FILE


def load_progress() -> int:
    """Return current stage (1..5). Creates file if missing."""
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
    """Write stage to progress.json."""
    data = {
        "stage": stage,
        "updated_at": datetime.now().isoformat(),
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def reset_progress() -> None:
    """Reset to stage 1."""
    save_progress(1)
