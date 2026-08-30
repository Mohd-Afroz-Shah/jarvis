"""
Brain Module

The main reasoning engine for J1.
Handles the agent loop: SEE -> UNDERSTAND -> ACT -> VERIFY

Uses the LLM to decide what tools to use, then executes them.
Continues until the user's task is complete.
"""

import json
import base64
from io import BytesIO
from PIL import Image
from llm import ask
from tool_executor import execute_tool
from tools import TOOLS

# SYSTEM_PROMPT = """
# You are J1, an AI assistant that controls a computer.

# Available tools:

# - open_app: open an application
# - read_screen: capture and inspect the current screen
# - read_ui: inspect the active application's UI controls
# - tap: click a location on the screen
# - type_text: type text using the keyboard
# - press_key: press an individual keyboard key
# - hotkey: press keyboard shortcuts
# - scroll: scroll the screen
# - wait: wait for an application or UI to update
# - click_ui: click a Windows UI element by its visible name
# - type_ui: enter text into a Windows text field by its visible name

# Rules:

# 1. Before using tap, use read_screen first.
# 2. Never guess coordinates.
# 3. When inspecting a screen, identify relevant UI elements.
# 4. Use the most recent screenshot when deciding where to tap.
# 5. After performing an action, read the screen again to verify the result.
# 6. Before using type_text, make sure the correct text field is focused.
# 7. Use press_key for individual keys.
# 8. Use hotkey for keyboard shortcuts such as Ctrl+S or Alt+F4.
# 9. Use wait when an application needs time to respond.
# 10. After important actions, use read_screen to verify the result.
# 11. When several actions can safely be performed together, you may call multiple tools in one response.
# 12. Do not batch actions that depend on seeing the result of a previous action.
# 13. After an important state-changing sequence, use read_screen to verify the result.
# 14. Use read_ui when interacting with structured Windows controls such as buttons, text fields, menus, lists, and dialogs.
# 15. Prefer read_ui over guessing coordinates when a suitable UI control is available.
# 16. Use read_screen when visual context is needed.
# 17. Prefer click_ui over tap when the desired control exists in read_ui.
# 18. Never use tap coordinates when a suitable UI element can be identified with read_ui.
# 19. Prefer type_ui over type_text when a suitable text field is available through read_ui.
# 20. Use type_text when the UI field cannot be reliably identified through the UI tree.
# 21. Before using type_ui, use read_ui to identify the correct text field.
# 22. If click_ui or type_ui reports multiple matching elements, do not guess. Use read_ui or read_screen to determine the correct element.
# 23. Prefer exact UI element matches over partial matches.
# 24. Execute safe independent actions together when possible.
# 25. Do not call read_screen or read_ui repeatedly if the current information is still valid.
# 26. For multi-step commands, first understand the complete goal and plan the required actions.
# 27. Avoid unnecessary read_screen and read_ui calls when the current UI state is already known.
# 28. After a successful action, continue with the next safe action when the required state is already known.
# 29. Only inspect the screen or UI again when the next action depends on a changed or unknown UI state.
# 30. For dialogs and state-changing operations such as Save As, inspect the new UI before interacting with it.
# 31. When save_file opens a dialog, always use read_ui to inspect the dialog before entering the filename.
# 32. Use the actual visible filename field and Save button from read_ui.
# 33. If an overwrite confirmation appears, inspect the UI again before confirming.
# 34. After saving, verify that the file was successfully saved before continuing.

# You should behave like an agent:
# SEE → UNDERSTAND → ACT → VERIFY.
# """

# def open_app(app_name: str):
#     """
#     J1 tool for opening an application.
#     """

#     action = Action(
#         name="open_app",
#         target=app_name
#     )

#     return execute_action(action)

# open_app_tool = types.FunctionDeclaration(
#     name="open_app",
#     description="Open an application on the computer.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "app_name": types.Schema(
#                 type="STRING",
#                 description="The name of the application to open."
#             )
#         },
#         required=["app_name"]
#     )
# )

# read_screen_tool = types.FunctionDeclaration(
#     name="read_screen",
#     description="""
#     Capture the current computer screen.

#     After receiving the screenshot, inspect it carefully.
#     Identify visible applications, buttons, text fields,
#     menus, icons, and other relevant UI elements.
#     """,
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={}
#     )
# )

# read_ui_tool = types.FunctionDeclaration(
#     name="read_ui",
#     description="""
#     Inspect the active Windows application's UI structure.
#     Returns useful interactive controls such as buttons,
#     text fields, menus, lists, tabs, and checkboxes.
#     Use this when interacting with structured Windows UI.
#     """,
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={}
#     )
# )

# click_ui_tool = types.FunctionDeclaration(
#     name="click_ui",
#     description="""
#     Click a Windows UI element by its visible name.
#     Use this instead of coordinates when a suitable UI element
#     is available in the UI tree.
#     """,
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "name": types.Schema(
#                 type="STRING",
#                 description="The visible name of the UI element to click."
#             ),
#             "control_type": types.Schema(
#                 type="STRING",
#                 description="Optional UI control type such as Button or MenuItem."
#             )
#         },
#         required=["name"]
#     )
# )

# type_ui_tool = types.FunctionDeclaration(
#     name="type_ui",
#     description="""
#     Enter text into a Windows text field identified by its visible name.
#     Use this instead of coordinates when the text field can be identified
#     through the UI structure.
#     """,
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "name": types.Schema(
#                 type="STRING",
#                 description="The visible name of the text field."
#             ),
#             "text": types.Schema(
#                 type="STRING",
#                 description="The exact text to enter."
#             )
#         },
#         required=["name", "text"]
#     )
# )

# tap_tool = types.FunctionDeclaration(
#     name="tap",
#     description="Click a specific location on the computer screen.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "x": types.Schema(
#                 type="INTEGER",
#                 description="Horizontal screen coordinate."
#             ),
#             "y": types.Schema(
#                 type="INTEGER",
#                 description="Vertical screen coordinate."
#             )
#         },
#         required=["x", "y"]
#     )
# )

# type_text_tool = types.FunctionDeclaration(
#     name="type_text",
#     description="Type text using the computer keyboard into the currently focused UI element.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "text": types.Schema(
#                 type="STRING",
#                 description="The exact text that should be typed."
#             )
#         },
#         required=["text"]
#     )
# )

# press_key_tool = types.FunctionDeclaration(
#     name="press_key",
#     description="Press a keyboard key such as Enter, Escape, Tab, or a modifier key.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "key": types.Schema(
#                 type="STRING",
#                 description="The keyboard key to press."
#             )
#         },
#         required=["key"]
#     )
# )

# hotkey_tool = types.FunctionDeclaration(
#     name="hotkey",
#     description="Press multiple keyboard keys together as a keyboard shortcut.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "keys": types.Schema(
#                 type="ARRAY",
#                 items=types.Schema(type="STRING"),
#                 description="Keys to press together, for example ['ctrl', 's']."
#             )
#         },
#         required=["keys"]
#     )
# )

# scroll_tool = types.FunctionDeclaration(
#     name="scroll",
#     description="Scroll the current screen vertically.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "amount": types.Schema(
#                 type="INTEGER",
#                 description="Positive value scrolls up, negative value scrolls down."
#             )
#         },
#         required=["amount"]
#     )
# )

# wait_tool = types.FunctionDeclaration(
#     name="wait",
#     description="Wait for a specified number of seconds.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "seconds": types.Schema(
#                 type="NUMBER",
#                 description="Number of seconds to wait."
#             )
#         },
#         required=["seconds"]
#     )
# )

# save_file_tool = types.FunctionDeclaration(
#     name="save_file",
#     description="Open the Save As dialog for the requested filename.",
#     parameters=types.Schema(
#         type="OBJECT",
#         properties={
#             "filename": types.Schema(
#                 type="STRING",
#                 description="The filename or path to save the current file as."
#             )
#         },
#         required=["filename"]
#     )
# )

# tools = types.Tool(
#     function_declarations=[
#         open_app_tool,
#         read_screen_tool,
#         read_ui_tool,
#         click_ui_tool,
#         type_ui_tool,
#         tap_tool,
#         type_text_tool,
#         press_key_tool,
#         hotkey_tool,
#         scroll_tool,
#         wait_tool,
#         save_file_tool
#     ]
# )

# chat = client.chats.create(
#     model="gemini-3.6-flash",
#     config=types.GenerateContentConfig(
#         system_instruction=SYSTEM_PROMPT,
#         tools=[tools]
#     )
# )

# def understand(command: str):

#     response = chat.send_message(command)

#     while response.function_calls:

#         function_responses = []

#         for function_call in response.function_calls:

#             print(
#                 f"\nJ1 decided to use tool: "
#                 f"{function_call.name}"
#             )

#             print(
#                 f"Arguments: "
#                 f"{function_call.args}"
#             )

#             if function_call.name == "open_app":

#                 app_name = function_call.args["app_name"]

#                 result = execute_action(
#                     Action(
#                         name="open_app",
#                         target=app_name
#                     )
#                 )

#             elif function_call.name == "read_screen":

#                 screenshot = read_screen()

#                 image_part = types.FunctionResponsePart(
#                     inline_data=types.FunctionResponseBlob(
#                         mime_type="image/png",
#                         data=screenshot
#                     )
#                 )

#                 function_responses.append(
#                     types.Part.from_function_response(
#                         name="read_screen",
#                         response={
#                             "result": "The current screen is attached."
#                         },
#                         parts=[image_part]
#                     )
#                 )

#                 print("Tool result: Screen captured.")
#                 continue

#             elif function_call.name == "read_ui":

#                 result = get_active_ui()

#                 print("Tool result: UI inspected.")

#                 function_responses.append(
#                     types.Part.from_function_response(
#                         name="read_ui",
#                         response={
#                             "result": result
#                         }
#                     )
#                 )

#                 continue

#             elif function_call.name == "click_ui":

#                 name = function_call.args["name"]
#                 control_type = function_call.args.get("control_type")

#                 result = click_ui(
#                     name,
#                     control_type
#                 )

#             elif function_call.name == "type_ui":

#                 name = function_call.args["name"]
#                 text = function_call.args["text"]

#                 result = type_ui(
#                     name,
#                     text
#                 )

#             elif function_call.name == "tap":

#                 x = function_call.args["x"]
#                 y = function_call.args["y"]

#                 result = tap(x, y)

#             elif function_call.name == "type_text":

#                 text = function_call.args["text"]

#                 result = type_text(text)

#             elif function_call.name == "press_key":

#                 key = function_call.args["key"]

#                 result = press_key(key)

#             elif function_call.name == "hotkey":

#                 keys = function_call.args["keys"]

#                 result = hotkey(*keys)

#             elif function_call.name == "scroll":

#                 amount = function_call.args["amount"]

#                 result = scroll(amount)

#             elif function_call.name == "wait":

#                 seconds = function_call.args["seconds"]

#                 result = wait(seconds)

#             elif function_call.name == "save_file":

#                 filename = function_call.args["filename"]

#                 result = save_file(filename)

#             else:

#                 result = f"Unknown tool: {function_call.name}"

#             print(f"Tool result: {result}")

#             function_responses.append(
#                 types.Part.from_function_response(
#                     name=function_call.name,
#                     response={
#                         "result": result
#                     }
#                 )
#             )

#         response = chat.send_message(
#             function_responses
#         )

#     if response.text:
#         print(f"\nJ1: {response.text}")

from llm import ask
from tools import TOOLS
from tool_executor import execute_tool


SYSTEM_PROMPT = """
You are J1, an AI computer-use agent.

Your job is to understand the user's request and control the computer.

You have access to tools that can:
- open applications
- inspect the UI
- inspect the screen
- click UI elements
- type text
- press keys
- use keyboard shortcuts
- scroll
- wait

Rules:

1. Never guess coordinates.
2. Prefer UI elements over coordinates.
3. Before clicking an unknown UI element, inspect the UI.
4. After an important state change, verify the result.
5. For multi-step tasks, complete the entire task.
6. Do not stop after completing only part of the request.
7. When the UI changes significantly, inspect it again.
8. Use the most recent UI/screen information.
9. Handle dialogs carefully.
10. Think like an agent: SEE → UNDERSTAND → ACT → VERIFY.
"""


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def understand(command):

    messages.append(
        {
            "role": "user",
            "content": command
        }
    )

    while True:

        response = ask(
            messages,
            TOOLS
        )

        message = response["message"]

        messages.append(message)

        # No tool call = J1 finished
        if not message.get("tool_calls"):
            print(f"\nJ1: {message.get('content', '')}")
            break

        for tool_call in message["tool_calls"]:

            name = tool_call["function"]["name"]
            args = tool_call["function"]["arguments"]

            print(f"\nJ1 decided to use tool: {name}")
            print(f"Arguments: {args}")

            result = execute_tool(
                name,
                args
            )

            print(f"Tool result: {result}")

            messages.append(
                {
                    "role": "tool",
                    "content": str(result)
                }
            )