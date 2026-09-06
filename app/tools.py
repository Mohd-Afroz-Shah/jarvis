try:
    from .actions import (
        Action,
        execute_action,
        read_screen,
        tap,
        type_text,
        press_key,
        hotkey,
        scroll,
        wait,
    )
    from .ui import (
        get_active_ui,
        click_ui,
        type_ui,
    )
    from .browser import (
        open_browser,
        navigate,
        browser_search,
        new_tab,
        close_tab,
        browser_back,
        browser_forward,
        refresh_page,
        reopen_closed_tab,
        get_browser_state,
    )
except ImportError:  # pragma: no cover - fallback for direct script execution
    from actions import (
        Action,
        execute_action,
        read_screen,
        tap,
        type_text,
        press_key,
        hotkey,
        scroll,
        wait,
    )
    from ui import (
        get_active_ui,
        click_ui,
        type_ui,
    )
    from browser import (
        open_browser,
        navigate,
        browser_search,
        new_tab,
        close_tab,
        browser_back,
        browser_forward,
        refresh_page,
        reopen_closed_tab,
        get_browser_state,
    )


def open_app(app_name):
    return execute_action(
        Action(
            name="open_app",
            target=app_name
        )
    )


def tool_open_app(app_name):
    return open_app(app_name)


def tool_read_screen():
    return read_screen()


def tool_read_ui():
    return get_active_ui()


def tool_click_ui(name, control_type=None):
    return click_ui(name, control_type)


def tool_type_ui(name, text):
    return type_ui(name, text)


def tool_tap(x, y):
    return tap(x, y)


def tool_type_text(text):
    return type_text(text)


def tool_press_key(key):
    return press_key(key)


def tool_hotkey(keys):
    return hotkey(*keys)


def tool_scroll(amount):
    return scroll(amount)


def tool_wait(seconds):
    return wait(seconds)


def tool_open_browser():
    return open_browser()


def tool_navigate(url):
    return navigate(url)


def tool_browser_search(query, site=""):
    return browser_search(query, site)


def tool_new_tab():
    return new_tab()


def tool_close_tab():
    return close_tab()


def tool_browser_back():
    return browser_back()


def tool_browser_forward():
    return browser_forward()


def tool_refresh_page():
    return refresh_page()


def tool_reopen_closed_tab():
    return reopen_closed_tab()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a Windows application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string"
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_screen",
            "description": "Capture the current screen.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_ui",
            "description": "Inspect the current Windows UI elements.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_ui",
            "description": "Click a visible UI element by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "control_type": {
                        "type": "string"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_ui",
            "description": "Type text into a visible UI element.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "text": {
                        "type": "string"
                    }
                },
                "required": ["name", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tap",
            "description": "Click screen coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text using the keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press a keyboard key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "hotkey",
            "description": "Press a keyboard shortcut.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Scroll the screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "integer"}
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Wait for an application to respond.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "number"}
                },
                "required": ["seconds"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Open and activate the browser using the existing Windows app launcher; do not reopen it if state says a browser is already open.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Navigate the browser to a URL. Use for direct navigation; do not repeat a search already completed by browser_search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_search",
            "description": "Search the current browser/site for a query. This changes the page to search results; do not call navigate to the same results afterward.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "site": {"type": "string", "description": "Optional target site, such as YouTube or Google."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "new_tab",
            "description": "Open a new browser tab and make it active.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_tab",
            "description": "Close the active browser tab; use only when the task requires closing it.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_back",
            "description": "Go back in browser history; this changes the current page.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_forward",
            "description": "Go forward in browser history; this changes the current page.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refresh_page",
            "description": "Refresh the active browser page; do not use as a substitute for a new search.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reopen_closed_tab",
            "description": "Reopen the last closed tab.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]