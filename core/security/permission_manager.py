from core.security.permission import Permission


class PermissionManager:

    def __init__(self):

        self.permissions = {

            # V1 permissions
            "computer_action": Permission(
                "computer_action",
                True
            ),

            "web_search": Permission(
                "web_search",
                True
            ),

            "phone_action": Permission(
                "phone_action",
                False
            ),

            # V2 permissions
            "computer_task": Permission(
                "computer_task",
                True
            ),

            "web_task": Permission(
                "web_task",
                True
            ),

            "youtube_task": Permission(
                "youtube_task",
                True
            ),

            "file_task": Permission(
                "file_task",
                True
            ),

            "browser_task": Permission(
                "browser_task",
                True
            ),
            "whatsapp_task": Permission(
                "whatsapp_task",
                True
            ),
        }

    def is_allowed(self, action: str) -> bool:

        permission = self.permissions.get(action)

        if permission is None:
            return False

        return permission.allowed

    def set_permission(
        self,
        action: str,
        allowed: bool
    ):

        if action in self.permissions:
            self.permissions[action].allowed = allowed
