"""
Planning Module - Phase 9

Multi-step command planning for J1.
Helps the agent break down complex commands into manageable steps.
"""

import re

from llm import ask
from task import J1Task, TaskStep


PLANNING_SYSTEM_PROMPT = """You are a planning assistant for J1, a Windows computer control agent.

Your job is to analyze complex user commands and create a step-by-step plan.

For each command, break it down into clear, sequential steps that J1 can follow.

Return your plan as a numbered list where each step is:
1. A clear description of what to do
2. What J1 should verify after each step

Example:
User: "Open Notepad, write hello, save as test.txt, close"

Plan:
1. Open Notepad
   - Verify: Notepad window is visible

2. Type "hello"
   - Verify: Text appears in the document

3. Save file as test.txt
   - Verify: Save dialog appears and file is saved

4. Close Notepad
   - Verify: Notepad window closes
"""


def analyze_command(user_command):
    """
    Analyze a user command to determine if it's multi-step.
    
    Args:
        user_command (str): The user's command
    
    Returns:
        dict: Analysis result with 'is_multi_step', 'steps', and 'tips'
    """
    
    # Simple heuristics for multi-step detection
    keywords = [
        "then", "after", "and ", "next", "save", "close",
        "write", "type", "click", "open", ",", ";"
    ]
    
    is_multi_step = any(keyword in user_command.lower() for keyword in keywords)
    
    return {
        "is_multi_step": is_multi_step,
        "command": user_command,
        "keywords_found": [k for k in keywords if k in user_command.lower()]
    }


def create_plan(user_command):
    """
    Create a detailed plan for a multi-step command.
    
    Args:
        user_command (str): The user's command
    
    Returns:
        str: A step-by-step plan
    """
    
    messages = [
        {
            "role": "user",
            "content": f"Please create a step-by-step plan for this command:\n\n{user_command}"
        }
    ]
    
    try:
        response = ask(messages)
        
        if isinstance(response, dict):
            content = response.get("message", {}).get("content", "")
            return content
        
        return str(response)
        
    except Exception as e:
        return f"Error creating plan: {str(e)}"


def should_create_plan(user_command):
    """
    Determine if a plan should be created for this command.
    
    Args:
        user_command (str): The user's command
    
    Returns:
        bool: Whether to create a plan
    """
    
    analysis = analyze_command(user_command)
    
    # If multi-step indicators found, create a plan
    if analysis["is_multi_step"]:
        return True
    
    # Also create a plan for long commands
    if len(user_command) > 100:
        return True
    
    return False


def create_structured_plan(user_command):
    """Create a compact structured plan for the current command."""
    command = user_command.strip()
    lower = command.lower()

    if not should_create_plan(command):
        return J1Task(command, [TaskStep(command)])

    steps = []
    app_match = re.search(r"(?:open|launch)\s+(?:the\s+)?([\w ]+?)(?:\s+and|\s*,|$)", command, re.I)
    if app_match:
        steps.append(TaskStep(f"Open {app_match.group(1).strip()}"))

    text_match = re.search(r"(?:write|type|enter)\s+(.+?)(?:\s*,|\s+then|\s+and\s+(?:save|close)|$)", command, re.I)
    if text_match:
        steps.append(TaskStep(f"Type {text_match.group(1).strip()}"))

    if "save" in lower:
        steps.append(TaskStep("Save the file"))
        steps.append(TaskStep("Verify the file was saved"))

    if "close" in lower:
        steps.append(TaskStep("Close the application"))
        steps.append(TaskStep("Verify the application is closed"))

    if not steps:
        clauses = [part.strip() for part in re.split(r",|\bthen\b|\band\b", command, flags=re.I) if part.strip()]
        steps = [TaskStep(clause) for clause in clauses]

    return J1Task(command, steps or [TaskStep(command)])


def get_planning_tips(user_command):
    """
    Get tips for completing a command.
    
    Args:
        user_command (str): The user's command
    
    Returns:
        list: List of planning tips
    """
    
    tips = []
    
    if "save" in user_command.lower():
        tips.append("After saving, verify the file appears in File Explorer")
    
    if "close" in user_command.lower():
        tips.append("Make sure to close all windows related to the task")
    
    if "type" in user_command.lower() or "write" in user_command.lower():
        tips.append("Verify text appears correctly before moving to next step")
    
    if "click" in user_command.lower():
        tips.append("Use read_ui to find the exact element before clicking")
    
    if any(app in user_command.lower() for app in ["chrome", "firefox", "browser"]):
        tips.append("Browsers take time to load, use wait() if needed")
    
    return tips
