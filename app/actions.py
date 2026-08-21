import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class Action:
    name: str
    target: Optional[str] = None
    value: Optional[str] = None


def execute_action(action: Action):
    print(f"\nExecuting action: {action.name}")

    if action.target:
        print(f"Target: {action.target}")

    if action.value:
        print(f"Value: {action.value}")

    if action.name == "open_app":
        open_app(action.target)


def open_app(app_name: Optional[str]):
    if not app_name:
        print("No application specified.")
        return

    apps = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
    }

    app_path = apps.get(app_name.lower())

    if not app_path:
        print(f"I don't know how to open {app_name} yet.")
        return

    try:
        subprocess.Popen(app_path)
        print(f"Opened {app_name}.")
    except Exception as error:
        print(f"Failed to open {app_name}: {error}")