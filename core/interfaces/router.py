from abc import ABC, abstractmethod


class IntentRouter(ABC):

    @abstractmethod
    def route(self, text: str) -> str:
        """Determine what Ela should do with the user's input."""
        pass