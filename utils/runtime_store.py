import json
import os
from typing import Dict, Any, Optional

RUNTIME_DIR = "data/runtime"
LAST_NEWSLETTER_FILE = os.path.join(RUNTIME_DIR, "last_newsletter.json")
LAST_METRICS_FILE = os.path.join(RUNTIME_DIR, "last_metrics.json")

def _ensure_dir():
    os.makedirs(RUNTIME_DIR, exist_ok=True)

def save_last_run(data: Dict[str, Any]) -> None:
    _ensure_dir()
    
    with open(LAST_NEWSLETTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    metrics_data = {
        "metrics": data.get("metrics", {}),
        "trust_metrics": data.get("trust_metrics"),
        "total_prompt_tokens": data.get("token_usage", {}).get("prompt_tokens", 0),
        "total_completion_tokens": data.get("token_usage", {}).get("completion_tokens", 0),
        "timings": data.get("timings", {})
    }
    
    with open(LAST_METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2, ensure_ascii=False)

def load_last_newsletter() -> Optional[Dict[str, Any]]:
    if not os.path.exists(LAST_NEWSLETTER_FILE):
        return None
    try:
        with open(LAST_NEWSLETTER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def load_last_metrics() -> Optional[Dict[str, Any]]:
    if not os.path.exists(LAST_METRICS_FILE):
        return None
    try:
        with open(LAST_METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
