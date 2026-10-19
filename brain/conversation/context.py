from core.interfaces.conversation_context import ConversationContextProvider


class ConversationContext(ConversationContextProvider):

    def __init__(self, max_messages: int = 20):
        self.messages = []
        self.max_messages = max_messages
        self.ui_target = {
            "name": None,
            "path": None,
            "x": None,
            "y": None,
            "url": None
        }
        self.browser_context = {
            "browser": None,
            "url": None
        }

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content
        })

        # Keep only recent conversation
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_messages(self):
        return self.messages

    def get_recent_messages(self, count: int = 10):
        return self.messages[-count:]

    def clear(self):
        self.messages.clear()
        self.ui_target = {
            "name": None,
            "path": None,
            "x": None,
            "y": None,
            "url": None
        }
        self.browser_context = {
            "browser": None,
            "url": None
        }

    def set_ui_target(
        self,
        name: str,
        path: str = None,
        x: int = None,
        y: int = None,
        url: str = None
    ):
        self.ui_target = {
            "name": name,
            "path": path,
            "x": x,
            "y": y,
            "url": url
        }

    def get_ui_target(self):
        return self.ui_target

    def set_browser_context(self, browser: str, url: str = None):
        self.browser_context = {
            "browser": browser,
            "url": url
        }

    def get_browser_context(self):
        return self.browser_context