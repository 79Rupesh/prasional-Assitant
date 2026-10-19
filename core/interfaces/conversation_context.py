from abc import ABC, abstractmethod


class ConversationContextProvider(ABC):

    @abstractmethod
    def add_message(self, role: str, content: str):
        pass

    @abstractmethod
    def get_messages(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def set_ui_target(
        self,
        name: str,
        path: str = None,
        x: int = None,
        y: int = None
    ):
        pass

    @abstractmethod
    def get_ui_target(self):
        pass

    @abstractmethod
    def set_browser_context(self, browser: str, url: str = None):
        pass

    @abstractmethod
    def get_browser_context(self):
        pass