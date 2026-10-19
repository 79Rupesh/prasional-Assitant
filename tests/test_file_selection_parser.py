from brain.task.file_selection_parser import FileSelectionParser


parser = FileSelectionParser()

tests = [
    "1",
    "2",
    "3",
    "one",
    "two",
    "three",
    "number 1",
    "number 3",
    "number three",
    "option 2",
    "option three",
    "first",
    "first one",
    "second",
    "third",
    "2nd one",
    "3rd one",
    "fourth",
    "10th one",
    "something else"
]

for text in tests:

    result = parser.parse(text)

    print(f"{text} -> {result}")