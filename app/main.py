from brain import understand


def main():

    print("J1 is alive.")
    print("Type 'exit' to stop J1.")

    while True:

        command = input("\nYou: ")

        if command.lower() == "exit":
            print("J1 shutting down.")
            break

        understand(command)


if __name__ == "__main__":
    main()