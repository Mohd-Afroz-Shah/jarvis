"""Structured runtime state for a J1 task."""

import json
from urllib.parse import unquote, urlparse
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
    browser_name: Optional[str] = None
    browser_open: bool = False
    browser_url: Optional[str] = None
    browser_title: Optional[str] = None
    search_query: Optional[str] = None
    search_site: Optional[str] = None
    search_completed: bool = False
    current_page_understood: bool = False
    browser_tab_count: int = 0
    browser_active_tab: int = 0
    successful_actions: Dict[str, Dict[str, Any]] = field(default_factory=dict)

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
            if self.browser_open and self.current_window:
                self.browser_title = self.current_window

    @staticmethod
    def action_signature(action: str, args: Dict[str, Any]) -> str:
        return f"{action}:{json.dumps(args or {}, sort_keys=True, default=str)}"

    def duplicate_action(self, action: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return a no-op result when an already-successful action is repeated."""
        app_name = str((args or {}).get("app_name", "")).lower()
        if action == "open_browser" and self.browser_open:
            return {
                "status": "already_done",
                "tool": action,
                "arguments": args or {},
                "message": "A browser is already open. Continue with the next task step.",
                "current_state": self.compact_context(),
            }
        if action == "open_app" and app_name in {"chrome", "firefox", "browser"} and self.browser_open:
            return {
                "status": "already_done",
                "tool": action,
                "arguments": args or {},
                "message": "The requested browser is already open. Continue with the next task step.",
                "current_state": self.compact_context(),
            }
        if action == "navigate" and self.search_completed and self.search_query:
            requested_url = str((args or {}).get("url", ""))
            if self.search_query.lower() in unquote(requested_url).lower():
                return {
                    "status": "already_done",
                    "tool": action,
                    "arguments": args or {},
                    "message": "The requested search results are already active. Continue with the next task step.",
                    "current_state": self.compact_context(),
                }

        signature = self.action_signature(action, args)
        if action == "browser_search":
            query = str((args or {}).get("query", ""))
            if not self.search_completed or query.lower() != str(self.search_query or "").lower():
                return None
        record = self.successful_actions.get(signature)
        if record is None:
            return None

        record["repeat_count"] = record.get("repeat_count", 0) + 1
        if record["repeat_count"] == 1:
            status = "already_done"
            message = "This exact action already succeeded. Continue with the next task step."
        else:
            status = "blocked"
            message = "This exact action is redundant and was blocked. Reconsider the remaining task steps."

        return {
            "status": status,
            "tool": action,
            "arguments": args or {},
            "message": message,
            "current_state": self.compact_context(),
        }

    def record_success(self, action: str, args: Dict[str, Any], result: Any):
        """Record a successful action and update facts used by the next decision."""
        signature = self.action_signature(action, args)
        self.successful_actions[signature] = {
            "result": str(result)[:500],
            "repeat_count": 0,
        }
        self.last_action = action
        self.last_action_result = str(result)[:500]
        self.last_error = None

        if action in ("open_browser", "open_app"):
            app_name = str(args.get("app_name", "")).lower()
            if action == "open_browser" or app_name in {"chrome", "firefox", "browser"}:
                self.browser_open = True
                self.browser_name = app_name or "chrome"
        elif action == "navigate":
            self.browser_open = True
            self.browser_url = args.get("url")
            self.search_completed = False
            self.current_page_understood = False
        elif action == "browser_search":
            self.browser_open = True
            self.search_query = args.get("query")
            self.search_completed = True
            self.current_page_understood = False
            site = str(args.get("site", "")).lower()
            if site in {"youtube", "youtube.com", "www.youtube.com"}:
                from urllib.parse import quote_plus
                self.search_site = "youtube.com"
                self.browser_url = f"https://www.youtube.com/results?search_query={quote_plus(str(self.search_query))}"
            elif self.browser_url:
                self.search_site = urlparse(self.browser_url).netloc or self.search_site
        elif action in ("browser_back", "browser_forward", "refresh_page", "new_tab", "close_tab"):
            self.current_page_understood = False
        elif action in ("read_ui", "read_screen"):
            self.current_page_understood = True

    def record_failure(self, action: str, args: Dict[str, Any], reason: Any):
        self.last_action = action
        self.last_action_result = str(reason)[:500]
        self.last_error = str(reason)[:500]
        self.task_status = "recovering"

    def compact_context(self) -> Dict[str, Any]:
        """Return only state relevant to the next model decision."""
        context = {
            "goal": self.goal,
            "current_application": self.current_application,
            "current_window": self.current_window,
            "browser_open": self.browser_open,
            "current_browser": self.browser_name,
            "current_url": self.browser_url,
            "current_page_title": self.browser_title,
            "search_query": self.search_query,
            "search_site": self.search_site,
            "search_completed": self.search_completed,
            "current_page_understood": self.current_page_understood,
            "last_action": self.last_action,
            "last_action_result": self.last_action_result,
            "last_error": self.last_error,
            "task_status": self.task_status,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps[-5:],
            "pending_steps": self.pending_steps[:5],
        }
        if self.browser_name:
            context.update({
                "browser_name": self.browser_name,
                "browser_url": self.browser_url,
                "browser_title": self.browser_title,
            })
        return context

    def to_dict(self):
        return asdict(self)
