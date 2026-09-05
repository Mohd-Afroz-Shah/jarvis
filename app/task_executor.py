"""Task execution adapter built on J1's existing tool executor."""

from typing import Any, Dict

from task import J1Task
from state import J1State
from tool_executor import execute_tool
from verifier import verify_action


MAX_STEP_ATTEMPTS = 3


def execute_task_tool(task: J1Task, state: J1State, tool_name: str, args: Dict[str, Any]):
    """Execute one existing J1 tool, update state, and verify its result."""
    task.mark_current_running()
    state.task_status = "running"
    state.update_action(tool_name, "running")

    try:
        result = execute_tool(tool_name, args)
        result_text = str(result)
        failed = result is None or result_text.lower().startswith(("failed", "i don't know", "unknown"))
        verification = verify_action(tool_name, result, state)
        success = not failed and verification.get("verified", False)

        if success:
            state.update_action(tool_name, result)
            if tool_name == "open_app":
                state.current_application = args.get("app_name")
            current = task.current_step
            if current and not current.description.lower().startswith("verify"):
                task.complete_current(result)
            elif current:
                task.complete_current(result)
        else:
            state.update_action(tool_name, result, result_text if failed else None)
            current = task.current_step
            if current and current.attempt_count >= MAX_STEP_ATTEMPTS:
                task.fail_current(result)
                state.task_status = "failed"

        return {
            "success": success,
            "result": result,
            "verification": verification,
        }
    except Exception as error:
        state.update_action(tool_name, "error", str(error))
        current = task.current_step
        if current and current.attempt_count >= MAX_STEP_ATTEMPTS:
            task.fail_current(str(error))
            state.task_status = "failed"
        return {
            "success": False,
            "result": f"Tool execution failed: {error}",
            "verification": {"verified": False, "method": "exception"},
        }
