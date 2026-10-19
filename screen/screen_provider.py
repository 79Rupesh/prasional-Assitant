from abc import ABC, abstractmethod


class ScreenProvider(ABC):

    @abstractmethod
    def capture(self, output_path: str) -> str:
        pass
    