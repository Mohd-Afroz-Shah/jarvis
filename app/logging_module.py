"""
Logging Module

Handles all J1 logging.
Logs user commands, tool usage, results, and errors.
"""

import os
import json
from datetime import datetime
from config import LOG_DIR


def get_log_filename():
    """Get the current log file path."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"j1_{date_str}.log")


def log_command(command):
    """Log a user command."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "command",
        "command": command
    }
    write_log(log_entry)


def log_tool_call(tool_name, tool_args):
    """Log a tool call."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "tool_call",
        "tool_name": tool_name,
        "tool_args": tool_args
    }
    write_log(log_entry)


def log_tool_result(tool_name, result, duration_ms=None):
    """Log a tool result."""
    # Don't log binary data (screenshots)
    if isinstance(result, bytes):
        result = "[Binary data - screenshot]"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "tool_result",
        "tool_name": tool_name,
        "result": str(result)[:500],  # Truncate long results
        "duration_ms": duration_ms
    }
    write_log(log_entry)


def log_error(error_msg, context=None):
    """Log an error."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "error",
        "error": error_msg,
        "context": context
    }
    write_log(log_entry)


def log_completion(status, message):
    """Log task completion."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "completion",
        "status": status,  # "success" or "failure"
        "message": message
    }
    write_log(log_entry)


def write_log(log_entry):
    """Write a log entry to the log file."""
    try:
        log_file = get_log_filename()
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Warning: Failed to write log: {str(e)}")
