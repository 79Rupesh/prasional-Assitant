from brain.task.browser_task_parser import BrowserTaskParser

parser = BrowserTaskParser()

commands = [
    "Open Chrome",
    "Open Google Chrome",
    "Chrome kholo",
    "Firefox kholo",
    "Open youtube.com",
    "Search for Python tutorials",
]

for command in commands:
    print(f"\nCommand: {command}")
    print("Result:", parser.parse(command))