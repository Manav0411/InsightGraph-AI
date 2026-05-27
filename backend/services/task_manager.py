import uuid
from typing import Dict, Any
from datetime import datetime

# Global in-memory dictionary to store active tasks
# Format: { "task_id": { "status": "running", "stage": "...", "progress": 0, "result": None, "error": None, "created_at": datetime } }
active_tasks: Dict[str, Dict[str, Any]] = {}

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
    return task_id

def update_task_stage(task_id: str, stage: str, progress: int = None):
    """Updates the stage and optionally the progress of a running task."""
    if task_id in active_tasks:
        active_tasks[task_id]["stage"] = stage
        if progress is not None:
            active_tasks[task_id]["progress"] = progress

def mark_task_completed(task_id: str, result: str = "success"):
    """Marks a task as completed successfully."""
    if task_id in active_tasks:
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["stage"] = "Done"
        active_tasks[task_id]["progress"] = 100
        active_tasks[task_id]["result"] = result

def mark_task_failed(task_id: str, error_message: str):
    """Marks a task as failed with an error message."""
    if task_id in active_tasks:
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["stage"] = "Error"
        active_tasks[task_id]["error"] = error_message

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Retrieves the current status of a task."""
    return active_tasks.get(task_id, None)

def cleanup_old_tasks():
    """Optional: Periodically clean up old tasks from memory."""
    # To prevent memory leaks over time, could remove tasks older than 24h
    pass
