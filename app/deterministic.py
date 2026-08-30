"""
Deterministic Actions Module - Phase 19

Simple, deterministic operations that don't require LLM reasoning.
Improves performance by bypassing the LLM for basic actions.
"""

import re
from actions import press_key, hotkey, wait, open_app


def parse_simple_command(command):
    """
    Parse a command to see if it can be handled deterministically.
    
    Returns:
        tuple: (can_handle, action_type, parameters)
    """
    
    command_lower = command.lower().strip()
    
    # Simple open app commands
    open_patterns = [
        (r'^open\s+(\w+)$', 'open_app'),
        (r'^open\s+the\s+(\w+)$', 'open_app'),
        (r'^launch\s+(\w+)$', 'open_app'),
    ]
    
    for pattern, action_type in open_patterns:
        match = re.match(pattern, command_lower)
        if match:
            app_name = match.group(1)
            return True, action_type, {"app_name": app_name}
    
    # Keyboard shortcuts
    shortcut_patterns = [
        (r'^save$|^save file$|^(ctrl\+s)$', 'hotkey', {"keys": ["ctrl", "s"]}),
        (r'^close$|^close app$|^close window$|^(alt\+f4)$', 'hotkey', {"keys": ["alt", "F4"]}),
        (r'^copy$|^(ctrl\+c)$', 'hotkey', {"keys": ["ctrl", "c"]}),
        (r'^paste$|^(ctrl\+v)$', 'hotkey', {"keys": ["ctrl", "v"]}),
        (r'^undo$|^(ctrl\+z)$', 'hotkey', {"keys": ["ctrl", "z"]}),
        (r'^redo$|^(ctrl\+y)$', 'hotkey', {"keys": ["ctrl", "y"]}),
        (r'^select all$|^(ctrl\+a)$', 'hotkey', {"keys": ["ctrl", "a"]}),
        (r'^print$|^(ctrl\+p)$', 'hotkey', {"keys": ["ctrl", "p"]}),
        (r'^find$|^(ctrl\+f)$', 'hotkey', {"keys": ["ctrl", "f"]}),
    ]
    
    for pattern, action_type, params in shortcut_patterns:
        if re.search(pattern, command_lower):
            return True, action_type, params
    
    # Special key presses
    special_keys = ["enter", "escape", "tab", "backspace", "delete", "space"]
    for key in special_keys:
        if f"press {key}" in command_lower or f"press the {key}" in command_lower:
            return True, "press_key", {"key": key}
    
    # Wait commands
    wait_pattern = r'^wait\s+(\d+)\s+(?:seconds?|secs?)?$'
    match = re.match(wait_pattern, command_lower)
    if match:
        seconds = int(match.group(1))
        return True, "wait", {"seconds": seconds}
    
    return False, None, {}


def execute_deterministic_action(action_type, parameters):
    """
    Execute a deterministic action without involving the LLM.
    
    Args:
        action_type (str): Type of action (open_app, hotkey, press_key, wait)
        parameters (dict): Action parameters
    
    Returns:
        tuple: (success, message)
    """
    
    try:
        if action_type == "open_app":
            app_name = parameters.get("app_name", "")
            open_app(app_name)
            return True, f"Opened {app_name}"
        
        elif action_type == "hotkey":
            keys = parameters.get("keys", [])
            hotkey(*keys)
            return True, f"Pressed {' + '.join(keys)}"
        
        elif action_type == "press_key":
            key = parameters.get("key", "")
            press_key(key)
            return True, f"Pressed {key}"
        
        elif action_type == "wait":
            seconds = parameters.get("seconds", 1)
            wait(seconds)
            return True, f"Waited {seconds} seconds"
        
        return False, f"Unknown action type: {action_type}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def should_use_deterministic_path(command):
    """
    Determine if we should use the deterministic path for a command.
    
    Args:
        command (str): User command
    
    Returns:
        bool: Whether to use deterministic path
    """
    
    can_handle, _, _ = parse_simple_command(command)
    return can_handle


def execute_simple_command(command):
    """
    Execute a simple command using the deterministic path.
    
    Args:
        command (str): User command
    
    Returns:
        tuple: (success, message)
    """
    
    can_handle, action_type, parameters = parse_simple_command(command)
    
    if not can_handle:
        return False, "Command cannot be handled deterministically"
    
    success, message = execute_deterministic_action(action_type, parameters)
    return success, message


# Command templates for common operations
COMMON_OPERATIONS = {
    "save": {
        "description": "Save current file",
        "deterministic": True,
        "action": ("hotkey", {"keys": ["ctrl", "s"]})
    },
    "close": {
        "description": "Close current window",
        "deterministic": True,
        "action": ("hotkey", {"keys": ["alt", "F4"]})
    },
    "copy": {
        "description": "Copy selected content",
        "deterministic": True,
        "action": ("hotkey", {"keys": ["ctrl", "c"]})
    },
    "paste": {
        "description": "Paste content",
        "deterministic": True,
        "action": ("hotkey", {"keys": ["ctrl", "v"]})
    },
    "undo": {
        "description": "Undo last action",
        "deterministic": True,
        "action": ("hotkey", {"keys": ["ctrl", "z"]})
    },
    "select_all": {
        "description": "Select all content",
        "deterministic": True,
        "action": ("hotkey", {"keys": ["ctrl", "a"]})
    },
}
