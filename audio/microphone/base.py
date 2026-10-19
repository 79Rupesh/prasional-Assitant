from abc import ABC, abstractmethod


class Microphone(ABC):

    @abstractmethod
    def record(self) -> bytes:
        """Record audio and return raw audio data."""
        pass