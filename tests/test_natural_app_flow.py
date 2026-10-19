from actions.task_dispatcher import TaskDispatcher


dispatcher = TaskDispatcher()


commands = [
    "Open my browser",
    "Open the calculator",
    "Launch Safari",
    "Start Terminal",
    "Close my browser",
    "Quit the calculator",
]


for command in commands:

    print()
    print(f"COMMAND: {command}")

    result = dispatcher.dispatch(
        "computer_task",
        command
    )

    print(f"ELA: {result}")