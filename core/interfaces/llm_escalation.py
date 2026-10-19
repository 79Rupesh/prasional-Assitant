from abc import ABC, abstractmethod


class LLMEscalationProvider(ABC):

    @abstractmethod
    def escalate(self, text: str, context: list) -> str:
        """Send a complex request to the LLM."""
        pass