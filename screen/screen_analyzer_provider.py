from abc import ABC, abstractmethod


class ScreenAnalyzerProvider(ABC):

    @abstractmethod
    def analyze(self, image_path: str) -> dict:
        pass