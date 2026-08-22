from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from actions import Action, execute_action, read_screen, tap


client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are J1, an AI assistant that controls a computer.

You have these tools:

- open_app: open an application
- read_screen: capture and inspect the current screen
- tap: click a location on the screen

IMPORTANT:
Before using tap, always use read_screen first.
Never guess screen coordinates.
Use coordinates only after inspecting the current screenshot.
"""

def open_app(app_name: str):
    """
    J1 tool for opening an application.
    """

    action = Action(
        name="open_app",
        target=app_name
    )

    return execute_action(action)

open_app_tool = types.FunctionDeclaration(
    name="open_app",
    description="Open an application on the computer.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "app_name": types.Schema(
                type="STRING",
                description="The name of the application to open."
            )
        },
        required=["app_name"]
    )
)

read_screen_tool = types.FunctionDeclaration(
    name="read_screen",
    description="Capture and inspect the current computer screen.",
    parameters=types.Schema(
        type="OBJECT",
        properties={}
    )
)

tap_tool = types.FunctionDeclaration(
    name="tap",
    description="Click a specific location on the computer screen.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "x": types.Schema(
                type="INTEGER",
                description="Horizontal screen coordinate."
            ),
            "y": types.Schema(
                type="INTEGER",
                description="Vertical screen coordinate."
            )
        },
        required=["x", "y"]
    )
)

tools = types.Tool(
    function_declarations=[
        open_app_tool,
        read_screen_tool,
        tap_tool
    ]
)

def understand(command: str):

    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            tools=[tools]
        )
    )

    response = chat.send_message(
        f"{SYSTEM_PROMPT}\n\nUser command: {command}"
    )

    while response.function_calls:

        function_responses = []

        for function_call in response.function_calls:

            print(
                f"\nJ1 decided to use tool: "
                f"{function_call.name}"
            )

            print(
                f"Arguments: "
                f"{function_call.args}"
            )

            if function_call.name == "open_app":

                result = open_app(
                    function_call.args["app_name"]
                )

                print(f"Tool result: {result}")

                function_responses.append(
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={
                            "result": result
                        }
                    )
                )

            elif function_call.name == "read_screen":

                screenshot = read_screen()

                print("Tool result: Screen captured.")

                image_part = types.FunctionResponsePart(
                    inline_data=types.FunctionResponseBlob(
                        mime_type="image/png",
                        data=screenshot,
                    )
                )

                function_responses.append(
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={
                            "result": "The current screen is attached."
                        },
                        parts=[image_part]
                    )
                )

            elif function_call.name == "tap":

                x = function_call.args["x"]
                y = function_call.args["y"]

                result = tap(x, y)

                print(f"Tool result: {result}")

                function_responses.append(
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={
                            "result": result
                        }
                    )
                )
        response = chat.send_message(
            function_responses
        )

    if response.text:
        print(f"\nJ1: {response.text}")