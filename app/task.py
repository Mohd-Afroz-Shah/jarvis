"""Task and step models used by the state-aware executor."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


STEP_STATUSES = {"pending", "running", "completed", "failed", "skipped"}


@dataclass
class TaskStep:
    description: str
    status: str = "pending"
    attempt_count: int = 0
    result: Any = None

    def set_status(self, status: str, result: Any = None):
        if status not in STEP_STATUSES:
            raise ValueError(f"Unknown step status: {status}")
        self.status = status
        if result is not None:
            self.result = result


@dataclass
class J1Task:
    goal: str
    steps: List[TaskStep] = field(default_factory=list)
    status: str = "planning"

    @property
    def is_complete(self) -> bool:
        return bool(self.steps) and all(
            step.status in ("completed", "skipped") for step in self.steps
        )

    @property
    def current_step(self):
        for step in self.steps:
            if step.status in ("pending", "running"):
                return step
        return None

    def mark_current_running(self):
        step = self.current_step
        if step:
            step.status = "running"
            step.attempt_count += 1
        return step

    def complete_current(self, result: Any = None):
        step = self.current_step
        if step:
            step.set_status("completed", result)
        if self.is_complete:
            self.status = "completed"

    def fail_current(self, result: Any = None):
        step = self.current_step
        if step:
            step.set_status("failed", result)
        self.status = "failed"

    def pending_descriptions(self) -> List[str]:
        return [step.description for step in self.steps if step.status == "pending"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "status": self.status,
            "steps": [
                {
                    "description": step.description,
                    "status": step.status,
                    "attempt_count": step.attempt_count,
                    "result": step.result,
                }
                for step in self.steps
            ],
        }
