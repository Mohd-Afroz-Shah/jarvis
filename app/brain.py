from google import genai
from config import GEMINI_API_KEY
from actions import Action


client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are J1, an AI assistant that controls devices through actions.

Available actions:

1. open_app
   - target: application name

2. unknown
   - use when the command cannot be understood

A user may request multiple actions.

Return ONE action per line using this exact format:

ACTION: <action_name>
TARGET: <target>

Examples:

User: Open Chrome
ACTION: open_app
TARGET: Chrome

User: Open Chrome and then Calculator
ACTION: open_app
TARGET: Chrome
ACTION: open_app
TARGET: Calculator
"""


def understand(command: str) -> list[Action]:
    prompt = f"""
{SYSTEM_PROMPT}

User command:
{command}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    text = response.text.strip()

    print(f"\nJ1 Brain Response:\n{text}\n")

    actions = []
    current_action = None
    current_target = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("ACTION:"):
            if current_action:
                actions.append(
                    Action(
                        name=current_action,
                        target=current_target
                    )
                )

            current_action = line.split(":", 1)[1].strip()
            current_target = None

        elif line.startswith("TARGET:"):
            current_target = line.split(":", 1)[1].strip()

    if current_action:
        actions.append(
            Action(
                name=current_action,
                target=current_target
            )
        )

    return actions