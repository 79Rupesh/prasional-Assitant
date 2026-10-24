"""In-memory task state for one Ela process only.

This intentionally has no file/database writes: restarting Ela discards all
task history, in line with the session-only memory requirement.
"""

from dataclasses import dataclass, field
from time import time
from uuid import uuid4


@dataclass
class TaskState:
    task_id: str
    task_type: str
    request: str
    status: str = "running"
    current_step: str = "dispatching"
    completed_steps: list[str] = field(default_factory=list)
    failure: str | None = None
    result: str | None = None
    created_at: float = field(default_factory=time)


class TaskStateManager:
    def __init__(self):
        self.tasks = {}
        self.active_task_id = None

    def start(self, task_type: str, request: str) -> TaskState:
        task = TaskState(str(uuid4()), task_type, request)
        self.tasks[task.task_id] = task
        self.active_task_id = task.task_id
        return task

    def finish(self, task: TaskState, result: str) -> TaskState:
        task.result = result
        result_lower = (result or "").lower()
        if "page load could not be verified" in result_lower:
            task.status = "unverified"
            task.current_step = "verification unavailable"
        elif result_lower.startswith(
            ("unable", "i couldn't", "i don't know", "permission denied", "unknown")
        ):
            task.status = "failed"
            task.current_step = "finished"
            task.failure = result
        else:
            task.status = "completed"
            task.current_step = "finished"
            task.completed_steps.append("handler returned a result")
        if self.active_task_id == task.task_id:
            self.active_task_id = None
        return task

    def fail(self, task: TaskState, error: Exception) -> TaskState:
        task.status = "failed"
        task.current_step = "failed"
        task.failure = f"{type(error).__name__}: {error}"
        if self.active_task_id == task.task_id:
            self.active_task_id = None
        return task

    def cancel_active(self) -> bool:
        if not self.active_task_id:
            return False
        task = self.tasks[self.active_task_id]
        task.status = "cancelled"
        task.current_step = "cancelled"
        self.active_task_id = None
        return True

    def get_active(self):
        return self.tasks.get(self.active_task_id)
