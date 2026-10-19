from abc import ABC, abstractmethod


class ActionDispatcher(ABC):

    @abstractmethod
    def dispatch(self, intent: str, text: str) -> str:
        """Dispatch a user request to the appropriate action."""
        pass