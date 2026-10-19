from brain.task.app_alias_resolver import AppAliasResolver


resolver = AppAliasResolver()


tests = [
    "browser",
    "web browser",
    "internet",
    "file manager",
    "file explorer",
    "code editor",
    "Safari",
    "Calculator",
]


for name in tests:

    result = resolver.resolve(name)

    print(f"{name} -> {result}")