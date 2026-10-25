from actions.task_dispatcher import TaskDispatcher


def main():
    dispatcher = TaskDispatcher()
    tasks = [
        ("computer_task", "Open Safari"),
        ("computer_task", "click on Explorer"),
        ("web_task", "Search Python tutorials"),
        ("youtube_task", "Search YouTube for music"),
        ("file_task", "Find my project folder"),
        ("conversation", "How are you?"),
    ]

    for task_type, text in tasks:
        result = dispatcher.dispatch(task_type, text)
        print(f"Task: {task_type}\nUser: {text}\nResult: {result}\n")


if __name__ == "__main__":
    main()
