from abc import ABC, abstractmethod


class STTProvider(ABC):

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio into text."""
        pass