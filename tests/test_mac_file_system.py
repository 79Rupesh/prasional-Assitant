from actions.file_system.mac_file_system import MacFileSystem


file_system = MacFileSystem()


print("Testing file search...")

results = file_system.find("Ela")

for result in results[:10]:
    print(result)


print()
print("Testing Desktop listing...")

desktop = file_system.list_directory("~/Desktop")

for item in desktop[:10]:
    print(item)