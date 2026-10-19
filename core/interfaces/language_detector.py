from abc import ABC, abstractmethod


class LanguageDetectorProvider(ABC):

    @abstractmethod
    def detect(self, text: str) -> str:
        """Detect the language of the given text."""
        pass