"""Browser automation tools using keyboard shortcuts and UI inspection."""

from urllib.parse import quote_plus

try:
    from .actions import hotkey, press_key, type_text, wait, open_app
    from .ui import get_active_ui
except ImportError:  # pragma: no cover - fallback for direct script execution
    from actions import hotkey, press_key, type_text, wait, open_app
    from ui import get_active_ui


def open_browser():
    """Open the default browser using the existing app launcher."""
    try:
        return open_app("chrome")
    except Exception as exc:
        return f"Failed to open browser: {exc}"


def navigate(url: str):
    """Navigate the active browser to a URL using Ctrl+L."""
    try:
        hotkey("ctrl", "l")
        wait(0.3)
        type_text(url, interval=0.01)
        press_key("enter")
        wait(1.5)
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Navigation failed: {e}"


def browser_search(query: str, site: str = ""):
    """Search the active browser or a requested site; this changes the current page."""
    try:
        hotkey("ctrl", "l")
        wait(0.3)
        normalized_site = site.strip().lower()
        if normalized_site in {"youtube", "youtube.com", "www.youtube.com"}:
            target = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        elif normalized_site in {"google", "google.com", "www.google.com"}:
            target = f"https://www.google.com/search?q={quote_plus(query)}"
        else:
            target = query
        type_text(target, interval=0.01)
        press_key("enter")
        wait(1.5)
        return f"Successfully searched for: {query}" + (f" on {site}" if site else "") + f". Results URL: {target}"
    except Exception as e:
        return f"Search failed: {e}"


def new_tab():
    """Open a new browser tab using Ctrl+T."""
    try:
        hotkey("ctrl", "t")
        wait(0.5)
        return "Successfully opened a new tab"
    except Exception as e:
        return f"Failed to open new tab: {e}"


def close_tab():
    """Close the active browser tab using Ctrl+W."""
    try:
        hotkey("ctrl", "w")
        wait(0.3)
        return "Successfully closed the active tab"
    except Exception as e:
        return f"Failed to close tab: {e}"


def browser_back():
    """Navigate back using Alt+Left."""
    try:
        hotkey("alt", "left")
        wait(1)
        return "Successfully navigated back"
    except Exception as e:
        return f"Back navigation failed: {e}"


def browser_forward():
    """Navigate forward using Alt+Right."""
    try:
        hotkey("alt", "right")
        wait(1)
        return "Successfully navigated forward"
    except Exception as e:
        return f"Forward navigation failed: {e}"


def refresh_page():
    """Refresh the page using Ctrl+R."""
    try:
        hotkey("ctrl", "r")
        wait(1)
        return "Successfully refreshed the page"
    except Exception as e:
        return f"Refresh failed: {e}"


def reopen_closed_tab():
    """Reopen the last closed tab using Ctrl+Shift+T."""
    try:
        hotkey("ctrl", "shift", "t")
        wait(0.5)
        return "Last closed tab reopened"
    except Exception as e:
        return f"Failed to reopen tab: {e}"


def get_browser_state() -> dict:
    """Get the current browser page state from UI inspection."""
    ui = get_active_ui()
    if isinstance(ui, dict) and "error" not in ui:
        return {
            "window": ui.get("window"),
            "url_detected": "address" in str(ui).lower(),
            "controls": len(ui.get("controls", [])),
        }
    return {"window": None, "url_detected": False, "controls": 0}
