"""
Main Module

Entry point for J1.
"""

from brain import understand
from logging_module import log_command, log_error


def main():
    """Main loop for J1 interactive mode."""
    
    print("\n" + "="*60)
    print("J1 - Windows AI Agent")
    print("="*60)
    print("\nType your command and press Enter.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            command = input("You: ").strip()
            
            if not command:
                continue
            
            if command.lower() == "exit":
                print("\nJ1 shutting down.")
                break
            
            # Log the command
            log_command(command)
            
            # Process the command
            understand(command)
            
        except KeyboardInterrupt:
            print("\n\nJ1 interrupted by user.")
            break
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"\n✗ {error_msg}")
            log_error(error_msg)


if __name__ == "__main__":
    main()
