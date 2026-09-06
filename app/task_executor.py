"""Task execution adapter built on J1's existing tool executor."""

from typing import Any, Dict

try:
    from .task import J1Task
    from .state import J1State
    from .tool_executor import execute_tool
    from .verifier import verify_action
except ImportError:  # pragma: no cover - fallback for direct script execution
    from task import J1Task
    from state import J1State
    from tool_executor import execute_tool
    from verifier import verify_action


MAX_STEP_ATTEMPTS = 3


def execute_task_tool(task: J1Task, state: J1State, tool_name: str, args: Dict[str, Any]):
    """Execute one existing J1 tool, update state, and verify its result."""
    duplicate = state.duplicate_action(tool_name, args)
    if duplicate is not None:
        if duplicate["status"] == "already_done":
            current = task.current_step
            if current:
                task.mark_current_running()
                task.complete_current(duplicate["message"])
                state.completed_steps = [
                    step.description
                    for step in task.steps
                    if step.status in ("completed", "skipped")
                ]
                state.pending_steps = task.pending_descriptions()
                state.current_step = len(state.completed_steps)
            state.update_action(tool_name, duplicate["message"])
        return {
            "success": duplicate["status"] == "already_done",
            "result": duplicate,
            "verification": {"verified": duplicate["status"] == "already_done", "method": "task_state"},
        }

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
            state.record_success(tool_name, args, result)
            if tool_name == "open_app":
                state.current_application = args.get("app_name")
            current = task.current_step
            if current and not current.description.lower().startswith("verify"):
                task.complete_current(result)
            elif current:
                task.complete_current(result)
            state.completed_steps = [
                step.description
                for step in task.steps
                if step.status in ("completed", "skipped")
            ]
            state.pending_steps = task.pending_descriptions()
            state.current_step = len(state.completed_steps)
            if task.is_complete:
                state.task_status = "completed"
        else:
            reason = result_text if failed else "Action result could not be verified"
            state.update_action(tool_name, result, reason)
            state.record_failure(tool_name, args, reason)
            current = task.current_step
            if current and current.attempt_count >= MAX_STEP_ATTEMPTS:
                task.fail_current(result)
                state.task_status = "failed"

            result = {
                "status": "failed",
                "tool": tool_name,
                "arguments": args,
                "reason": reason,
                "current_state": state.compact_context(),
            }

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
            "result": {
                "status": "failed",
                "tool": tool_name,
                "arguments": args,
                "reason": str(error),
                "current_state": state.compact_context(),
            },
            "verification": {"verified": False, "method": "exception"},
        }
