class ConfirmationManager:

    def __init__(self):
        self.pending_action = None

    def request_confirmation(self, action: str, target: str) -> str:

        self.pending_action = {
            "action": action,
            "target": target
        }

        if action == "whatsapp_send":
            return (
                f"I staged the file for {target}. "
                "Should I send it now? Say yes or no."
            )

        return (
            f"Are you sure you want to {action} "
            f"{target}? Please say yes or no."
        )

    def confirm(self) -> bool:

        if self.pending_action is None:
            return False

        self.pending_action = None

        return True

    def cancel(self):

        self.pending_action = None

    def has_pending(self) -> bool:

        return self.pending_action is not None

    def get_pending(self):

        return self.pending_action
