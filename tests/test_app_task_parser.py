from brain.task.app_task_parser import AppTaskParser


parser = AppTaskParser()


tests = [
    "Open my browser",
    "Open the browser",
    "Open my Safari",
    "Close the calculator",
    "Launch VS Code",
    "Quit my browser",
]


for text in tests:

    result = parser.parse(text)

    print(f"{text} -> {result}")