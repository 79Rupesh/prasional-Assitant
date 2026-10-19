from core.security.permission_manager import PermissionManager


manager = PermissionManager()


tests = [
    "computer_task",
    "web_task",
    "youtube_task",
    "file_task",
    "phone_action",
    "unknown_task",
]


for task in tests:

    result = manager.is_allowed(task)

    print(f"{task}: {result}")