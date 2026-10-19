class SecurityPolicy:

    CONFIRMATION_REQUIRED = {
        "delete",
        "move",
        "rename",
    }

    def requires_confirmation(self, action: str) -> bool:

        return action in self.CONFIRMATION_REQUIRED