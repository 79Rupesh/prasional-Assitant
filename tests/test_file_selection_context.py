from brain.task.file_selection_context import FileSelectionContext


context = FileSelectionContext()

results = [
    "/Users/test/resume.pdf",
    "/Users/test/project/resume.pdf",
    "/Users/test/old/resume.pdf"
]

context.set_results(results)

print("Stored results:")
print(context.get_results())

context.clear()

print()
print("After clear:")
print(context.get_results())