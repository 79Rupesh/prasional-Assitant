from actions.task_dispatcher import TaskDispatcher


def main():
    dispatcher = TaskDispatcher()
    print("Step 1: Open README\n")
    print(dispatcher.dispatch("file_task", "Open README"))
    print("\nStep 2: Select third result\n")
    print(dispatcher.dispatch("file_task", "3rd one"))


if __name__ == "__main__":
    main()
