"""
Brain Module

The main reasoning engine for J1.
Handles the agent loop: SEE -> UNDERSTAND -> ACT -> VERIFY

Uses the LLM to decide what tools to use, then executes them.
Continues until the user's task is complete.
"""

import json
import base64
import re
import time
from io import BytesIO
from PIL import Image

try:
    from .llm import ask
    from .tools import TOOLS
    from .planning import create_structured_plan
    from .state import J1State
    from .task_executor import execute_task_tool
except ImportError:  # pragma: no cover - fallback for direct script execution
    from llm import ask
    from tools import TOOLS
    from planning import create_structured_plan
    from state import J1State
    from task_executor import execute_task_tool


SYSTEM_PROMPT = """You are J1, a Windows computer-use agent.

Your job is to understand natural language commands and complete them using your tools.

**Available Tools:**
- open_app: Open an application or folder (e.g., "notepad", "chrome", "calculator", "explorer", "downloads")
- open_browser: Open the active browser
- navigate: Navigate the active browser to a URL
- browser_search: Search the active browser for a query
- new_tab: Open a new browser tab
- close_tab: Close the active browser tab
- browser_back: Go back in browser history
- browser_forward: Go forward in browser history
- refresh_page: Refresh the active page
- read_screen: Capture and inspect the current screen
- read_ui: Inspect the active application's UI controls
- click_ui: Click a Windows UI element by its visible name
- type_ui: Enter text into a Windows text field by its visible name
- tap: Click screen coordinates (use only after reading screen)
- type_text: Type text using the keyboard
- press_key: Press a keyboard key
- hotkey: Press keyboard shortcuts (e.g., Ctrl+S)
- scroll: Scroll the screen
- wait: Wait for an application to respond

**Critical Rules:**

1. **Understand the complete goal first.** For multi-step commands, plan all steps before starting.
2. **Always prefer UI automation over coordinates.** Use read_ui to find elements, then click_ui.
3. **Never guess coordinates.** Always read_screen first, then identify coordinates from the screenshot.
4. **Read UI before clicking unknown elements.** If unsure where to click, use read_ui.
5. **Verify important actions.** After significant state changes, use read_screen to verify.
6. **Handle dialogs carefully.** Inspect dialogs with read_ui before interacting.
7. **Be efficient.** Don't repeatedly read screen/UI if you already have the information.
8. **Use keyboard shortcuts.** Ctrl+S for save, Ctrl+C/V for copy/paste, Alt+F4 to close, etc.
9. **Handle errors gracefully.** If a tool fails, read the current state and try an alternative.
10. **Continue until complete.** Multi-step tasks must be fully completed, not abandoned after one action.
11. **No confirmation loops.** For normal operations, proceed directly. Only ask for confirmation on destructive actions.
12. **Use wait() for slow apps.** Some applications need time to load (Office, browsers, etc.).
13. **Use task state.** Before every action, consider the goal, current state, completed steps, remaining steps, and latest result.
14. **Do not repeat successful actions.** If state says an app is open or a search is active, continue with the next unfinished step.
15. **browser_search changes the current page to search results.** Do not call navigate to the same search-results URL afterward.
16. **read_ui is information gathering only.** Never click a control merely because it appears in the UI tree.
17. **Only click relevant controls.** The control must directly contribute to the current task; ignore suggestions, ads, unrelated buttons, and browser chrome.
18. **Treat already_done as progress.** Choose the next remaining task step instead of retrying that action.

**Agent Loop Pattern:**
1. SEE - Understand what's on screen using read_screen or read_ui
2. UNDERSTAND - Decide what action to take
3. ACT - Execute the tool
4. VERIFY - Confirm the result, adjust if needed
5. REPEAT until complete

When you have completed the user's task, respond with a clear completion message.
If a task is impossible, explain why clearly.
"""


def convert_image_to_base64(image_bytes):
    """Convert image bytes to base64 for the LLM."""
    try:
        return base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        return None


def format_screenshot_for_llm(screenshot_bytes):
    """
    Format screenshot bytes as a message for the LLM.
    
    For Ollama, we need to embed images differently.
    Since Ollama doesn't support image input directly in this way,
    we'll return a note that a screenshot was captured.
    """
    if screenshot_bytes:
        try:
            img = Image.open(BytesIO(screenshot_bytes))
            img_b64 = convert_image_to_base64(screenshot_bytes)
            return f"[Screenshot captured: {img.width}x{img.height} pixels]"
        except Exception as e:
            return f"[Screenshot captured but could not be processed]"
    return None


def format_elapsed_time(seconds):
    """Format elapsed request time as hours, minutes, and seconds."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"


def execute_agent_loop(user_command, max_iterations=20):
    """
    Execute the main agent loop.
    
    SEE -> UNDERSTAND -> ACT -> VERIFY
    
    Args:
        user_command (str): The user's natural language command
        max_iterations (int): Maximum number of tool calls to prevent infinite loops
    
    Returns:
        str: The final response from the agent
    """
    
    request_started = time.perf_counter()

    task = create_structured_plan(user_command)
    state = J1State(
        goal=user_command,
        task_status="running",
        pending_steps=task.pending_descriptions(),
    )

    print("Goal:")
    print(f"  {user_command}")
    if len(task.steps) > 1:
        print("Plan:")
        for index, step in enumerate(task.steps, 1):
            print(f"  {index}. {step.description}")

    # Initialize conversation history
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\nFor each action, call the appropriate tool immediately. Do not explain your reasoning.",
        },
        {
            "role": "user",
            "content": user_command
        }
    ]
    
    iteration = 0
    repeated_tools = []  # Track repeated tool calls
    executed_any_tool = False
    
    print(f"\n{'='*60}")
    print(f"User: {user_command}")
    print(f"{'='*60}\n")
    
    while iteration < max_iterations:
        iteration += 1
        
        try:
            # Get LLM response
            print(f"[Iteration {iteration}/{max_iterations}] Asking LLM...")
            state.pending_steps = task.pending_descriptions()
            state.current_step = len(task.steps) - len(state.pending_steps)
            messages.append({
                "role": "user",
                "content": (
                    "Before choosing the next action, use this current task context: "
                    f"{state.compact_context()}"
                ),
            })
            response = ask(messages, tools=TOOLS)
            
            # Ollama returns ChatResponse, whose structured actions live at
            # response.message.tool_calls. Do not inspect message.thinking or
            # parse model text as an action.
            if isinstance(response, dict):
                message = response.get("message", {})
                content = message.get("content", "")
                tool_calls = message.get("tool_calls", [])
            else:
                message = getattr(response, "message", None)
                if message is None:
                    print(f"Unexpected response type: {type(response)}")
                    final_response = str(response)
                    print(f"\n{'='*60}")
                    print(f"J1: {final_response}")
                    print(f"Response time: {format_elapsed_time(time.perf_counter() - request_started)}")
                    print(f"{'='*60}\n")
                    return final_response

                content = getattr(message, "content", "") or ""
                tool_calls = getattr(message, "tool_calls", None) or []

            # A normal assistant response with no structured tool calls ends
            # the current request. Thinking text is intentionally ignored.
            if not tool_calls:
                if task.is_complete or not executed_any_tool:
                    task.status = "completed" if task.is_complete else task.status
                    state.task_status = task.status
                    print(f"Task status: {state.task_status}")
                    print(f"Current step: {len(task.steps) - len(task.pending_descriptions())} / {len(task.steps)}")
                    print(f"\n{'='*60}")
                    print(f"J1: {content}")
                    print(f"Response time: {format_elapsed_time(time.perf_counter() - request_started)}")
                    print(f"{'='*60}\n")
                    return content

                state.task_status = "recovering"
                messages.append({
                    "role": "user",
                    "content": f"The task is not verified complete. Current state: {state.compact_context()}. Continue with the next required action.",
                })
                continue

            state.task_status = "running"
            state.current_step = len(task.steps) - len(task.pending_descriptions()) + 1

            # Execute each tool call
            tool_call_results = []
            normalized_tool_args = []
            
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    function = tool_call.get("function", {})
                    tool_name = function.get("name", "")
                    tool_args = function.get("arguments", {})
                    tool_call_id = tool_call.get("id")
                    tool_call_type = tool_call.get("type", "function")
                else:
                    function = tool_call.function
                    tool_name = function.name
                    tool_args = function.arguments
                    tool_call_id = getattr(tool_call, "id", None)
                    tool_call_type = getattr(tool_call, "type", "function")

                if isinstance(tool_args, str):
                    tool_args = json.loads(tool_args)

                # Infer the requested site from the user's goal when the local
                # model omits the optional browser_search site argument.
                if tool_name == "browser_search" and not tool_args.get("site"):
                    site_match = re.search(
                        r"search\s+(?:the\s+)?([^,]+?)\s+for\s+",
                        user_command,
                        re.IGNORECASE,
                    )
                    if site_match:
                        tool_args["site"] = site_match.group(1).strip()

                normalized_tool_args.append(tool_args)
                
                print(f"🔧 Tool: {tool_name}")
                print(f"📦 Args: {tool_args}")
                
                # Check for repeated tool calls (loop detection)
                tool_sig = f"{tool_name}:{json.dumps(tool_args, sort_keys=True)}"
                if tool_sig in repeated_tools:
                    print("    WARNING: Repeated tool call detected; state-aware guard will prevent redundant execution")
                else:
                    repeated_tools.append(tool_sig)
                
                # Execute the tool
                try:
                    execution = execute_task_tool(task, state, tool_name, tool_args)
                    result = execution["result"]
                    executed_any_tool = True
                    
                    # Handle screenshot data
                    if tool_name == "read_screen" and isinstance(result, bytes):
                        result_text = format_screenshot_for_llm(result)
                        tool_call_results.append({
                            "tool_name": tool_name,
                            "result": result_text,
                            "tool_call_id": tool_call_id,
                            "verification": execution["verification"],
                        })
                    else:
                        tool_call_results.append({
                            "tool_name": tool_name,
                            "result": result,
                            "tool_call_id": tool_call_id,
                            "verification": execution["verification"],
                        })
                    
                    # Print result summary
                    if isinstance(result, bytes):
                        print(f"    ✓ Executed (screenshot data)")
                    else:
                        result_str = str(result)[:100]
                        print(f"    ✓ Executed: {result_str}")
                        
                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    print(f"    ✗ Error: {error_msg}")
                    tool_call_results.append({
                        "tool_name": tool_name,
                        "result": error_msg,
                        "tool_call_id": tool_call_id,
                        "verification": {"verified": False, "method": "exception"},
                    })
            
            # Preserve the assistant's structured tool calls so Ollama can
            # associate the following tool messages with its request.
            assistant_tool_calls = []
            for call_index, call in enumerate(tool_calls):
                call_function = call.get("function", {}) if isinstance(call, dict) else call.function
                call_id = (
                    call.get("id") if isinstance(call, dict) else getattr(call, "id", None)
                ) or f"call_{iteration}_{call_index}"
                call_arguments = json.dumps(normalized_tool_args[call_index] or {})
                assistant_tool_calls.append({
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": (
                            call_function.get("name", "")
                            if isinstance(call_function, dict)
                            else getattr(call_function, "name", "")
                        ),
                        "arguments": call_arguments,
                    },
                })

            assistant_message = {
                "role": "assistant",
                "content": content,
                "tool_calls": assistant_tool_calls,
            }
            messages.append(assistant_message)
            
            # Add tool results
            for result_index, tool_result in enumerate(tool_call_results):
                tool_message = {
                    "role": "tool",
                    "content": f"Tool '{tool_result['tool_name']}' result: {tool_result['result']}"
                }
                tool_message["tool_call_id"] = (
                    tool_result.get("tool_call_id")
                    or assistant_tool_calls[result_index]["id"]
                )
                messages.append(tool_message)

            state.pending_steps = task.pending_descriptions()
            state.current_step = len(task.steps) - len(state.pending_steps)
            messages.append({
                "role": "user",
                "content": f"J1 task state: {state.compact_context()}",
            })
            
        except Exception as e:
            error_msg = f"Error in agent loop: {str(e)}"
            print(f"✗ {error_msg}")
            print(f"Response time: {format_elapsed_time(time.perf_counter() - request_started)}")
            return f"{error_msg}. The request stopped to prevent repeated execution."
    
    # Max iterations reached
    print(f"\n{'='*60}")
    print("J1: Maximum iterations reached. Unable to complete task.")
    print(f"Response time: {format_elapsed_time(time.perf_counter() - request_started)}")
    print(f"{'='*60}\n")
    return "Error: Maximum tool call iterations reached without completing the task."


def understand(command: str):
    """
    Main entry point for the brain.
    Process a user command and execute the agent loop.
    
    Args:
        command (str): Natural language command from user
    """
    try:
        response = execute_agent_loop(command)
        return response
    except Exception as e:
        error_msg = f"Fatal error in brain: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg
