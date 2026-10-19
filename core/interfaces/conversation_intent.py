from abc import ABC, abstractmethod


class ConversationIntentProvider(ABC):

    @abstractmethod
    def detect(self, text: str) -> str:
        """Detect the conversational intent of the given text."""
        pass