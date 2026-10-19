from brain.task.file_task_parser import FileTaskParser


parser = FileTaskParser()


tests = [
    "Find my Ela folder",
    "Open my Ela folder",
    "Find the project",
    "Open the file",
]


for text in tests:

    result = parser.parse(text)

    print(f"{text}")
    print(result)
    print()