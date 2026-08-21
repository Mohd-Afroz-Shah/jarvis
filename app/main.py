from brain import understand
from actions import execute_action


def main():
    print("J1 is alive.")
    print("Type 'exit' to stop J1.")

    while True:
        command = input("\nYou: ")

        if command.lower() == "exit":
            print("J1 shutting down.")
            break

        actions = understand(command)

        for action in actions:
            execute_action(action)

if __name__ == "__main__":
    main()