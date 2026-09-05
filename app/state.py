"""Structured runtime state for a J1 task."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class J1State:
    goal: str
    current_application: Optional[str] = None
    current_window: Optional[str] = None
    current_ui: Optional[Dict[str, Any]] = None
    last_action: Optional[str] = None
    last_action_result: Optional[str] = None
    last_error: Optional[str] = None
    task_status: str = "planning"
    current_step: int = 0
    completed_steps: List[str] = field(default_factory=list)
    pending_steps: List[str] = field(default_factory=list)

    def update_action(self, action: str, result: Any, error: Optional[str] = None):
        self.last_action = action
        self.last_action_result = str(result)[:500]
        self.last_error = error
        if error:
            self.task_status = "recovering"

    def update_ui(self, ui_data: Any):
        if isinstance(ui_data, dict):
            self.current_ui = ui_data
            self.current_window = ui_data.get("window") or self.current_window

    def compact_context(self) -> Dict[str, Any]:
        """Return only state relevant to the next model decision."""
        return {
            "goal": self.goal,
            "current_application": self.current_application,
            "current_window": self.current_window,
            "last_action": self.last_action,
            "last_action_result": self.last_action_result,
            "last_error": self.last_error,
            "task_status": self.task_status,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps[-5:],
            "pending_steps": self.pending_steps[:5],
        }

    def to_dict(self):
        return asdict(self)
