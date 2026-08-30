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
    }
]