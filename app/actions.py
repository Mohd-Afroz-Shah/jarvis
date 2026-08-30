import subprocess
from dataclasses import dataclass
from typing import Optional
from PIL import ImageGrab
from io import BytesIO
import pyautogui


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
        return open_app(action.target)

    return f"Unknown action: {action.name}"


def open_app(app_name: Optional[str]):
    if not app_name:
        return "No application specified."

    apps = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
    }

    app_path = apps.get(app_name.lower())

    if not app_path:
        return f"I don't know how to open {app_name} yet."

    try:
        subprocess.Popen(app_path)
        return f"Successfully opened {app_name}."

    except Exception as error:
        return f"Failed to open {app_name}: {error}"

def read_screen():
    screenshot = ImageGrab.grab()

    buffer = BytesIO()
    screenshot.save(buffer, format="PNG")

    return buffer.getvalue()

def tap(x: int, y: int):
    try:
        pyautogui.click(x, y)

        return f"Successfully clicked at ({x}, {y})."

    except Exception as error:
        return f"Failed to click: {error}"

def type_text(text: str):
    try:
        pyautogui.write(text, interval=0.02)

        return f"Successfully typed: {text}"

    except Exception as error:
        return f"Failed to type text: {error}"

def press_key(key: str):
    try:
        pyautogui.press(key)

        return f"Successfully pressed {key}."

    except Exception as error:
        return f"Failed to press key: {error}"

def hotkey(*keys: str):
    try:
        pyautogui.hotkey(*keys)

        return f"Successfully pressed {' + '.join(keys)}."

    except Exception as error:
        return f"Failed to press hotkey: {error}"


def scroll(amount: int):
    try:
        pyautogui.scroll(amount)

        return f"Successfully scrolled {amount}."

    except Exception as error:
        return f"Failed to scroll: {error}"


def wait(seconds: float):
    try:
        import time
        time.sleep(seconds)

        return f"Waited for {seconds} seconds."

    except Exception as error:
        return f"Failed to wait: {error}"

def save_file(filename: str):
    """
    Open Save As and prepare the requested filename.
    """
    hotkey("ctrl", "shift", "s")
    wait(1)

    return f"Save dialog opened. Requested filename: {filename}"