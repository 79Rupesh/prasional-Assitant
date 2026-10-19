from brain.task.local_classifier import LocalTaskClassifier


classifier = LocalTaskClassifier()


tests = [
    "Open Safari",
    "Close Calculator",
    "Search Python tutorials",
    "Find my project folder",
    "Open this file",
    "Search YouTube for music",
    "How are you?",
    "Tell me something about AI",
]


for text in tests:
    task_type = classifier.classify(text)

    print(f"User: {text}")
    print(f"Task: {task_type}")
    print()
    