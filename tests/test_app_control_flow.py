from actions.task_dispatcher import TaskDispatcher


dispatcher = TaskDispatcher()


tests = [
    "Open Safari",
    "Launch Calculator",
    "Start Terminal",
    "Close Safari",
    "Quit Calculator",
    "Exit Terminal",
    "Open SomeRandomApp123",
]


for command in tests:

    print()
    print(f"Command: {command}")

    result = dispatcher.dispatch(
        "computer_task",
        command
    )

    print(f"Result: {result}")