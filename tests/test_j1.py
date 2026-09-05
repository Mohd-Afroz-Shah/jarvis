"""
J1 Test Suite - Phase 22-23

Integration tests for J1 computer control agent.
Tests basic functionality and multi-step commands.
"""

import sys
import os
import time

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from brain import understand
from actions import read_screen, wait
from ui import get_active_ui
from planning import create_structured_plan
from state import J1State
from task import J1Task, TaskStep


class TestResult:
    """Track test results."""
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.message = ""
        self.duration = 0
    
    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.name} ({self.duration:.1f}s) - {self.message}"


def run_test(test_name, test_func):
    """Run a single test."""
    result = TestResult(test_name)
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"{'='*60}")
        
        test_func()
        result.passed = True
        result.message = "Completed successfully"
        
    except AssertionError as e:
        result.message = str(e)
    except Exception as e:
        result.message = f"Error: {str(e)}"
    finally:
        result.duration = time.time() - start_time
    
    print(f"\n{result}")
    return result


# ============================================================================
# BASIC TOOL TESTS
# ============================================================================

def test_read_screen():
    """Test: Capture screenshot."""
    screenshot = read_screen()
    assert isinstance(screenshot, bytes), "Screenshot should be bytes"
    assert len(screenshot) > 0, "Screenshot should not be empty"
    print(f"Screenshot captured: {len(screenshot)} bytes")


def test_read_ui():
    """Test: Inspect UI elements."""
    ui = get_active_ui()
    assert isinstance(ui, dict), "UI result should be dict"
    assert "window" in ui or "error" in ui, "UI should have window or error"
    if "window" in ui:
        print(f"Active window: {ui['window']}")
        print(f"Controls found: {len(ui.get('controls', []))}")


def test_wait():
    """Test: Wait function."""
    start = time.time()
    wait(1)
    elapsed = time.time() - start
    assert 0.9 < elapsed < 1.5, "Wait should be approximately 1 second"
    print(f"Wait test completed in {elapsed:.2f}s")


def test_structured_plan():
    """Test: Multi-step commands produce explicit task steps."""
    task = create_structured_plan(
        "Open Notepad, write Hello, save it as test.txt and close Notepad"
    )
    assert len(task.steps) >= 5, "Expected a structured multi-step plan"
    assert task.steps[0].description == "Open Notepad"
    assert all(step.status == "pending" for step in task.steps)
    print(f"Structured plan created with {len(task.steps)} steps")


def test_state_updates():
    """Test: Task and runtime state track progress explicitly."""
    task = J1Task("Open Notepad", [TaskStep("Open Notepad")])
    state = J1State("Open Notepad", pending_steps=task.pending_descriptions())
    task.mark_current_running()
    state.update_action("open_app", "Successfully opened Notepad")
    state.current_application = "Notepad"
    task.complete_current("Successfully opened Notepad")
    state.pending_steps = task.pending_descriptions()
    state.task_status = task.status
    assert task.is_complete
    assert state.current_application == "Notepad"
    assert state.last_action == "open_app"
    assert state.task_status == "completed"
    print("State transition completed successfully")


# ============================================================================
# APPLICATION TESTS
# ============================================================================

def test_open_notepad():
    """Test 1: Open Notepad."""
    command = "Open Notepad"
    print(f"Command: {command}")
    understand(command)
    wait(2)
    
    ui = get_active_ui()
    print(f"Active window: {ui.get('window', 'Unknown')}")


def test_open_calculator():
    """Test 2: Open Calculator."""
    command = "Open Calculator"
    print(f"Command: {command}")
    understand(command)
    wait(2)
    
    ui = get_active_ui()
    print(f"Active window: {ui.get('window', 'Unknown')}")


# ============================================================================
# MULTI-STEP COMMAND TESTS
# ============================================================================

def test_notepad_write():
    """Test 3: Open Notepad and write text."""
    command = "Open Notepad and write 'Hello from J1'"
    print(f"Command: {command}")
    understand(command)
    wait(2)


def test_notepad_save():
    """Test 4: Open Notepad, write, save, and close."""
    command = "Open Notepad, write 'J1 Test File', save it as J1Test.txt, then close Notepad"
    print(f"Command: {command}")
    understand(command)
    wait(3)


# ============================================================================
# SCREEN INSPECTION TESTS
# ============================================================================

def test_read_screen_command():
    """Test 5: Use read_screen tool through agent."""
    command = "Read my screen and describe what you see"
    print(f"Command: {command}")
    understand(command)


# ============================================================================
# CHROME TESTS
# ============================================================================

def test_open_chrome():
    """Test 6: Open Chrome."""
    command = "Open Chrome"
    print(f"Command: {command}")
    understand(command)
    wait(5)  # Chrome takes longer to load


# ============================================================================
# TEST SUITE MANAGEMENT
# ============================================================================

def run_basic_tests():
    """Run basic tool tests."""
    print("\n" + "="*60)
    print("PHASE 22-23: J1 TEST SUITE")
    print("Basic Tool Tests")
    print("="*60)
    
    results = []
    
    results.append(run_test("Screenshot Capture", test_read_screen))
    results.append(run_test("UI Inspection", test_read_ui))
    results.append(run_test("Wait Function", test_wait))
    results.append(run_test("Structured Planning", test_structured_plan))
    results.append(run_test("State Updates", test_state_updates))
    
    return results


def run_application_tests():
    """Run application tests."""
    print("\n" + "="*60)
    print("Application Tests")
    print("="*60)
    
    results = []
    
    results.append(run_test("Open Notepad", test_open_notepad))
    results.append(run_test("Open Calculator", test_open_calculator))
    
    return results


def run_integration_tests():
    """Run multi-step integration tests."""
    print("\n" + "="*60)
    print("Integration Tests (Multi-Step Commands)")
    print("="*60)
    
    results = []
    
    results.append(run_test("Notepad Write Text", test_notepad_write))
    results.append(run_test("Notepad Save File", test_notepad_save))
    results.append(run_test("Screen Inspection", test_read_screen_command))
    
    return results


def print_test_summary(all_results):
    """Print summary of all test results."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in all_results if r.passed)
    failed = sum(1 for r in all_results if not r.passed)
    total = len(all_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\nFailed Tests:")
        for result in all_results:
            if not result.passed:
                print(f"  - {result.name}: {result.message}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="J1 Test Suite")
    parser.add_argument("--suite", choices=["basic", "apps", "integration", "all"], 
                       default="basic", help="Test suite to run")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run tests one by one with pauses")
    
    args = parser.parse_args()
    
    results = []
    
    if args.suite in ["basic", "all"]:
        results.extend(run_basic_tests())
        if args.interactive:
            input("\nPress Enter to continue to application tests...")
    
    if args.suite in ["apps", "all"]:
        results.extend(run_application_tests())
        if args.interactive:
            input("\nPress Enter to continue to integration tests...")
    
    if args.suite in ["integration", "all"]:
        results.extend(run_integration_tests())
    
    print_test_summary(results)
