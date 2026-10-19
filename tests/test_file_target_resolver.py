from actions.file_system.mac_file_target_resolver import (
    MacFileTargetResolver
)


resolver = MacFileTargetResolver()


tests = [
    "Ela",
    "Desktop",
    "Downloads",
]


for target in tests:

    print(f"Searching: {target}")

    results = resolver.resolve(target)

    for result in results[:5]:
        print(result)

    print()