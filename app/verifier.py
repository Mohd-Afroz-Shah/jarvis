"""Lightweight verification helpers for J1 actions."""

import os
from typing import Any, Dict

try:
    from .ui import get_active_ui
except ImportError:  # pragma: no cover - fallback for direct script execution
    from ui import get_active_ui


def verify_action(action_name: str, result: Any, state=None) -> Dict[str, Any]:
    """Verify an action using the cheapest available signal."""
    result_text = str(result).lower()

    if action_name == "open_app":
        ui = get_active_ui()
        if isinstance(ui, dict) and "error" not in ui:
            if state is not None:
                state.update_ui(ui)
            return {"verified": True, "method": "read_ui", "details": ui.get("window")}
        return {"verified": "successfully opened" in result_text, "method": "result"}

    if action_name in ("read_ui", "read_screen"):
        return {"verified": result is not None, "method": action_name}

    if action_name in ("type_text", "type_ui"):
        return {"verified": "failed" not in result_text, "method": "result"}

    if action_name in (
        "hotkey", "press_key", "tap", "click_ui", "scroll", "wait",
        "open_browser", "navigate", "browser_search", "browser_back",
        "browser_forward", "new_tab", "close_tab", "refresh_page",
        "reopen_closed_tab",
    ):
        return {"verified": "failed" not in result_text, "method": "result"}

    return {"verified": False, "method": "unknown"}


def verify_file_saved(path: str) -> Dict[str, Any]:
    exists = os.path.isfile(os.path.expanduser(path))
    return {"verified": exists, "method": "filesystem", "path": path}
