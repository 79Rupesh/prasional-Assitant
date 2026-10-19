from abc import ABC, abstractmethod


class TTSProvider(ABC):

    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text into speech."""
        pass