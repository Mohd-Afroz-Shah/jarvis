"""
Security Module - Phase 21

Security hardening for J1.
Prevents dangerous operations:
- File deletion
- Dangerous command execution
- Password/credential access
- System modification
"""

import os
import re

try:
    from .config import ALLOW_FILE_DELETE, ALLOW_FILE_WRITE, ALLOW_EXTERNAL_COMMANDS
except ImportError:  # pragma: no cover - fallback for direct script execution
    from config import ALLOW_FILE_DELETE, ALLOW_FILE_WRITE, ALLOW_EXTERNAL_COMMANDS


# Dangerous file patterns
DANGEROUS_PATHS = [
    r"C:\\Windows\\",
    r"C:\\Program Files",
    r"C:\\System32",
    r"C:\\ProgramData",
]

# Dangerous keywords in commands
DANGEROUS_KEYWORDS = [
    "format",
    "delete",
    "rm -rf",
    "del /s",
    "taskkill",
    "shutdown",
    "restart",
    "reboot",
    "virus",
    "malware",
    "credential",
    "password",
    "secret",
    "token",
]


def is_path_dangerous(path):
    """Check if a file path is in a protected system directory."""
    path_lower = path.lower()
    for dangerous_pattern in DANGEROUS_PATHS:
        if re.search(dangerous_pattern.lower(), path_lower):
            return True
    return False


def validate_file_operation(operation, filepath):
    """
    Validate a file operation.
    
    Args:
        operation (str): "read", "write", "delete"
        filepath (str): Path to file
    
    Returns:
        tuple: (is_safe, message)
    """
    
    if operation == "delete":
        if not ALLOW_FILE_DELETE:
            return False, "File deletion is disabled. Enable ALLOW_FILE_DELETE=true in .env"
        
        if is_path_dangerous(filepath):
            return False, f"Cannot delete files in protected directory: {filepath}"
        
        return True, "Safe to delete"
    
    elif operation == "write":
        if not ALLOW_FILE_WRITE:
            return False, "File writing is disabled. Enable ALLOW_FILE_WRITE=true in .env"
        
        if is_path_dangerous(filepath):
            return False, f"Cannot write to protected directory: {filepath}"
        
        return True, "Safe to write"
    
    elif operation == "read":
        # Reading is generally safe
        if is_path_dangerous(filepath):
            return False, f"Cannot read from protected directory: {filepath}"
        
        return True, "Safe to read"
    
    return False, f"Unknown operation: {operation}"


def validate_command(command):
    """
    Validate a shell command for dangerous operations.
    
    Args:
        command (str): Command to validate
    
    Returns:
        tuple: (is_safe, message)
    """
    
    if not ALLOW_EXTERNAL_COMMANDS:
        return False, "External command execution is disabled. Enable ALLOW_EXTERNAL_COMMANDS=true in .env"
    
    command_lower = command.lower()
    
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in command_lower:
            return False, f"Command contains dangerous keyword: {keyword}"
    
    return True, "Safe command"


def validate_tool_call(tool_name, tool_args):
    """
    Validate a tool call for security issues.
    
    Args:
        tool_name (str): Name of the tool
        tool_args (dict): Arguments for the tool
    
    Returns:
        tuple: (is_safe, message)
    """
    
    # Check tool-specific security rules
    if tool_name == "open_app":
        app_name = tool_args.get("app_name", "").lower()
        
        # Allow common safe applications
        safe_apps = ["notepad", "calculator", "chrome", "firefox", "explorer", "powershell"]
        if any(safe in app_name for safe in safe_apps):
            return True, "Safe application"
        
        # Check against dangerous patterns
        if "system32" in app_name or "cmd.exe" in app_name:
            return False, "Cannot open system applications directly"
        
        return True, "Application allowed"
    
    elif tool_name == "type_text":
        text = tool_args.get("text", "")
        
        # Check for dangerous commands being typed
        if any(keyword in text.lower() for keyword in ["http://", "https://"]):
            # URLs are generally ok
            return True, "URL allowed"
        
        return True, "Text allowed"
    
    elif tool_name == "tap":
        # Coordinate clicks are generally safe once the screen is inspected
        return True, "Click allowed"
    
    elif tool_name == "read_screen" or tool_name == "read_ui":
        # Inspection is always safe
        return True, "Inspection allowed"
    
    return True, "Tool allowed by default"


def log_security_event(event_type, details, allowed=False):
    """
    Log a security event.
    
    Args:
        event_type (str): Type of event (e.g., "blocked_operation")
        details (str): Details of what was attempted
        allowed (bool): Whether the operation was allowed
    """
    from logging_module import write_log
    
    log_entry = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "event": "security",
        "event_type": event_type,
        "details": details,
        "allowed": allowed
    }
    
    write_log(log_entry)
