from pywinauto import Desktop


def get_active_ui():
    try:
        desktop = Desktop(backend="uia")

        windows = desktop.windows()

        active_window = None

        for window in windows:
            try:
                if window.is_active():
                    active_window = window
                    break
            except Exception:
                continue

        if active_window is None:
            return {
                "error": "Could not find the active window."
            }

        result = {
            "window": active_window.window_text(),
            "controls": []
        }

        for control in active_window.descendants():

            try:
                name = control.window_text()
                control_type = control.element_info.control_type

                useful_types = {
                    "Button",
                    "Edit",
                    "Text",
                    "MenuItem",
                    "CheckBox",
                    "RadioButton",
                    "ComboBox",
                    "List",
                    "ListItem",
                    "Tab",
                    "Hyperlink"
                }

                if name and control_type in useful_types:
                    result["controls"].append({
                        "name": name,
                        "type": control_type
                    })

            except Exception:
                continue

        return result

    except Exception as error:
        return {
            "error": str(error)
        }

def click_ui(name: str, control_type: str | None = None):
    try:
        desktop = Desktop(backend="uia")

        active_window = None

        for window in desktop.windows():
            try:
                if window.is_active():
                    active_window = window
                    break
            except Exception:
                continue

        if active_window is None:
            return "Could not find the active window."

        target = name.strip().lower()
        matches = []

        for control in active_window.descendants():

            try:
                control_name = control.window_text().strip()
                current_type = control.element_info.control_type

                if not control_name:
                    continue

                name_matches = (
                    control_name.lower() == target
                    or target in control_name.lower()
                )

                type_matches = (
                    control_type is None
                    or current_type.lower() == control_type.lower()
                )

                if name_matches and type_matches:
                    matches.append(control)

            except Exception:
                continue

        if not matches:
            return f"Could not find UI element: {name}"

        if len(matches) > 1:
            options = [
                f"{c.window_text()} ({c.element_info.control_type})"
                for c in matches
            ]

            return (
                f"Multiple UI elements found for '{name}'. "
                f"Options: {options}"
            )

        control = matches[0]

        control.click_input()

        return (
            f"Successfully clicked '{control.window_text()}' "
            f"({control.element_info.control_type})."
        )

    except Exception as error:
        return f"Failed to click UI element: {error}"
    
def type_ui(name: str, text: str):
    try:
        desktop = Desktop(backend="uia")

        active_window = None

        for window in desktop.windows():
            try:
                if window.is_active():
                    active_window = window
                    break
            except Exception:
                continue

        if active_window is None:
            return "Could not find the active window."

        target = name.strip().lower()
        matches = []

        for control in active_window.descendants():

            try:
                control_name = control.window_text().strip()
                control_type = control.element_info.control_type

                if (
                    control_name
                    and target in control_name.lower()
                    and control_type == "Edit"
                ):
                    matches.append(control)

            except Exception:
                continue

        if not matches:
            return f"Could not find text field: {name}"

        if len(matches) > 1:
            options = [
                c.window_text()
                for c in matches
            ]

            return (
                f"Multiple text fields found for '{name}'. "
                f"Options: {options}"
            )

        control = matches[0]

        control.click_input()
        control.set_edit_text(text)

        return f"Successfully entered text into '{control.window_text()}'."

    except Exception as error:
        return f"Failed to type into UI element: {error}"
        
if __name__ == "__main__":
    import pprint

    pprint.pprint(get_active_ui())