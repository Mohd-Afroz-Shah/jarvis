try:
    from .tools import (
        tool_open_app,
        tool_open_browser,
        tool_read_screen,
        tool_read_ui,
        tool_click_ui,
        tool_type_ui,
        tool_tap,
        tool_type_text,
        tool_press_key,
        tool_hotkey,
        tool_scroll,
        tool_wait,
        tool_navigate,
        tool_browser_search,
        tool_new_tab,
        tool_close_tab,
        tool_browser_back,
        tool_browser_forward,
        tool_refresh_page,
        tool_reopen_closed_tab,
    )
except ImportError:  # pragma: no cover - fallback for direct script execution
    from tools import (
        tool_open_app,
        tool_open_browser,
        tool_read_screen,
        tool_read_ui,
        tool_click_ui,
        tool_type_ui,
        tool_tap,
        tool_type_text,
        tool_press_key,
        tool_hotkey,
        tool_scroll,
        tool_wait,
        tool_navigate,
        tool_browser_search,
        tool_new_tab,
        tool_close_tab,
        tool_browser_back,
        tool_browser_forward,
        tool_refresh_page,
        tool_reopen_closed_tab,
    )


def execute_tool(name, args):
    args = args or {}

    handlers = {
        "open_app": lambda: tool_open_app(args["app_name"]),
        "open_browser": lambda: tool_open_browser(),
        "read_screen": lambda: tool_read_screen(),
        "read_ui": lambda: tool_read_ui(),
        "click_ui": lambda: tool_click_ui(args.get("name"), args.get("control_type")),
        "type_ui": lambda: tool_type_ui(args.get("name"), args.get("text")),
        "tap": lambda: tool_tap(args["x"], args["y"]),
        "type_text": lambda: tool_type_text(args.get("text", "")),
        "press_key": lambda: tool_press_key(args.get("key", "")),
        "hotkey": lambda: tool_hotkey(args.get("keys", [])),
        "scroll": lambda: tool_scroll(args.get("amount", 0)),
        "wait": lambda: tool_wait(args.get("seconds", 0)),
        "navigate": lambda: tool_navigate(args.get("url", "")),
        "browser_search": lambda: tool_browser_search(args.get("query", ""), args.get("site", "")),
        "new_tab": lambda: tool_new_tab(),
        "close_tab": lambda: tool_close_tab(),
        "browser_back": lambda: tool_browser_back(),
        "browser_forward": lambda: tool_browser_forward(),
        "refresh_page": lambda: tool_refresh_page(),
        "reopen_closed_tab": lambda: tool_reopen_closed_tab(),
    }

    if name in handlers:
        return handlers[name]()

    return f"Unknown tool: {name}"