import uuid
import json
import os
from typing import Dict, Any
from datetime import datetime

TASKS_FILE = os.path.join(os.path.dirname(__file__), "..", ".tasks.json")

# Global in-memory dictionary to store active tasks
# Format: { "task_id": { "status": "running", "stage": "...", "progress": 0, "result": None, "error": None, "created_at": datetime } }
active_tasks: Dict[str, Dict[str, Any]] = {}

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                data = json.load(f)
            for task in data.values():
                if "created_at" in task and isinstance(task["created_at"], str):
                    try:
                        task["created_at"] = datetime.fromisoformat(task["created_at"])
                    except ValueError:
                        pass
            active_tasks.clear()
            active_tasks.update(data)
        except Exception:
            active_tasks.clear()

def save_tasks():
    export_tasks = {}
    for tid, task in active_tasks.items():
        task_copy = task.copy()
        if "created_at" in task_copy and isinstance(task_copy["created_at"], datetime):
            task_copy["created_at"] = task_copy["created_at"].isoformat()
        export_tasks[tid] = task_copy
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(export_tasks, f)
    except Exception:
        pass

def create_task() -> str:
    """Creates a new task and returns its ID."""
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "status": "running",
        "stage": "Initializing...",
        "progress": 0,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow()
    }
    save_tasks()
    return task_id

def update_task_stage(task_id: str, stage: str, progress: int = None):
    """Updates the stage and optionally the progress of a running task."""
    if task_id in active_tasks:
        active_tasks[task_id]["stage"] = stage
        if progress is not None:
            active_tasks[task_id]["progress"] = progress
        save_tasks()

def mark_task_completed(task_id: str, result: str = "success"):
    """Marks a task as completed successfully."""
    if task_id in active_tasks:
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["stage"] = "Done"
        active_tasks[task_id]["progress"] = 100
        active_tasks[task_id]["result"] = result
        save_tasks()

def mark_task_failed(task_id: str, error_message: str):
    """Marks a task as failed with an error message."""
    if task_id in active_tasks:
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["stage"] = "Error"
        active_tasks[task_id]["error"] = error_message
        save_tasks()

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Retrieves the current status of a task."""
    return active_tasks.get(task_id, None)

def cleanup_old_tasks():
    """Optional: Periodically clean up old tasks from memory."""
    pass
