from abc import ABC, abstractmethod


class TaskClassifierProvider(ABC):

    @abstractmethod
    def classify(self, text: str) -> str:
        """Classify a user request into a task category."""
        pass