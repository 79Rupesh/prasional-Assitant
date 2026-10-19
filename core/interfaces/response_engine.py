from abc import ABC, abstractmethod


class ResponseEngineProvider(ABC):

    @abstractmethod
    def generate(
        self,
        text: str,
        language: str,
        context: list
    ) -> str:
        """Generate a local response."""
        pass