import json
import os
from typing import Dict, Any, Optional

RUNTIME_DIR = "data/runtime"
LAST_RUN_FILE = os.path.join(RUNTIME_DIR, "last_run.json")

def _ensure_dir():
    os.makedirs(RUNTIME_DIR, exist_ok=True)

def save_last_run(data: Dict[str, Any]) -> None:
    """
    Persist the latest pipeline run (NewsletterResponse dict) to disk.
    """
    _ensure_dir()
    with open(LAST_RUN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_last_run() -> Optional[Dict[str, Any]]:
    """
    Load the latest pipeline run from disk. Returns None if it doesn't exist.
    """
    if not os.path.exists(LAST_RUN_FILE):
        return None
    try:
        with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
