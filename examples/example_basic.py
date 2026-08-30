"""
Example Scripts - J1 Usage Examples

These examples demonstrate how to use J1 for various tasks.
Run from the project root: python examples/example_basic.py
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../app'))

from brain import understand
from actions import wait


def example_1_open_app():
    """Example 1: Open an application."""
    print("\n" + "="*60)
    print("Example 1: Opening an Application")
    print("="*60)
    
    command = "Open Notepad"
    print(f"\nCommand: '{command}'")
    print("Expected: Notepad opens")
    
    understand(command)
    wait(2)


def example_2_read_screen():
    """Example 2: Read and describe the screen."""
    print("\n" + "="*60)
    print("Example 2: Reading the Screen")
    print("="*60)
    
    command = "What's currently on my screen? Describe it in detail."
    print(f"\nCommand: '{command}'")
    print("Expected: J1 reads the screen and describes what it sees")
    
    understand(command)


def example_3_type_text():
    """Example 3: Type text in Notepad."""
    print("\n" + "="*60)
    print("Example 3: Typing Text")
    print("="*60)
    
    command = "Type 'Hello from J1' in Notepad"
    print(f"\nCommand: '{command}'")
    print("Expected: Text appears in Notepad")
    
    understand(command)
    wait(1)


def example_4_save_file():
    """Example 4: Save a file."""
    print("\n" + "="*60)
    print("Example 4: Saving a File")
    print("="*60)
    
    command = "Save the current file as example.txt in the Documents folder"
    print(f"\nCommand: '{command}'")
    print("Expected: File is saved")
    
    understand(command)
    wait(1)


def example_5_multi_step():
    """Example 5: Multi-step command."""
    print("\n" + "="*60)
    print("Example 5: Multi-Step Command")
    print("="*60)
    
    command = """
    Open Notepad, write 'This is a J1 test file', 
    save it as j1_example.txt in the Desktop folder, 
    then close Notepad.
    """
    print(f"\nCommand: '{command.strip()}'")
    print("Expected: Complete task without stopping after each step")
    
    understand(command)
    wait(2)


def example_6_use_ui():
    """Example 6: Interact with UI elements."""
    print("\n" + "="*60)
    print("Example 6: UI Interaction")
    print("="*60)
    
    command = "Open Calculator and add 5 and 3"
    print(f"\nCommand: '{command}'")
    print("Expected: Calculator opens, performs calculation")
    
    understand(command)
    wait(1)


def example_7_error_recovery():
    """Example 7: Handle errors gracefully."""
    print("\n" + "="*60)
    print("Example 7: Error Recovery")
    print("="*60)
    
    command = "Try to open a nonexistent application called MyFakeApp"
    print(f"\nCommand: '{command}'")
    print("Expected: J1 handles the error gracefully and reports it")
    
    understand(command)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="J1 Usage Examples")
    parser.add_argument("--example", type=int, choices=[1, 2, 3, 4, 5, 6, 7],
                       help="Run specific example (1-7)")
    parser.add_argument("--all", action="store_true", 
                       help="Run all examples sequentially")
    parser.add_argument("--pause", action="store_true",
                       help="Pause between examples")
    
    args = parser.parse_args()
    
    examples = [
        example_1_open_app,
        example_2_read_screen,
        example_3_type_text,
        example_4_save_file,
        example_5_multi_step,
        example_6_use_ui,
        example_7_error_recovery,
    ]
    
    if args.example:
        # Run specific example
        examples[args.example - 1]()
    elif args.all:
        # Run all examples
        for i, example in enumerate(examples, 1):
            try:
                example()
                if args.pause and i < len(examples):
                    input("\nPress Enter to continue to next example...")
            except Exception as e:
                print(f"Error in example {i}: {e}")
    else:
        # Default: show usage
        print("\nJ1 Usage Examples")
        print("="*60)
        print("\nAvailable examples:")
        print("  1. Open an application")
        print("  2. Read and describe the screen")
        print("  3. Type text in an application")
        print("  4. Save a file")
        print("  5. Multi-step command (open, write, save, close)")
        print("  6. Interact with UI elements (Calculator)")
        print("  7. Error recovery (handle missing apps)")
        print("\nUsage:")
        print("  python examples/example_basic.py --example 1    # Run example 1")
        print("  python examples/example_basic.py --all          # Run all examples")
        print("  python examples/example_basic.py --all --pause  # Run all with pauses")
