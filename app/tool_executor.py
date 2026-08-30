from tools import (
    tool_open_app,
    tool_read_screen,
    tool_read_ui,
    tool_click_ui,
    tool_type_ui,
    tool_tap,
    tool_type_text,
    tool_press_key,
    tool_hotkey,
    tool_scroll,
    tool_wait,
)


def execute_tool(name, args):

    if name == "open_app":
        return tool_open_app(args["app_name"])

    if name == "read_screen":
        return tool_read_screen()

    if name == "read_ui":
        return tool_read_ui()

    if name == "click_ui":
        return tool_click_ui(
            args["name"],
            args.get("control_type")
        )

    if name == "type_ui":
        return tool_type_ui(
            args["name"],
            args["text"]
        )

    if name == "tap":
        return tool_tap(
            args["x"],
            args["y"]
        )

    if name == "type_text":
        return tool_type_text(args["text"])

    if name == "press_key":
        return tool_press_key(args["key"])

    if name == "hotkey":
        return tool_hotkey(args["keys"])

    if name == "scroll":
        return tool_scroll(args["amount"])

    if name == "wait":
        return tool_wait(args["seconds"])

    return f"Unknown tool: {name}"