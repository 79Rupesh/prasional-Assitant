from actions.task_dispatcher import TaskDispatcher


dispatcher = TaskDispatcher()


print("Step 1: Open README")
print()

result = dispatcher.dispatch(
    "file_task",
    "Open README"
)

print(result)

print()
print("Step 2: Select third result")
print()

result = dispatcher.dispatch(
    "file_task",
    "3rd one"
)

print(result)