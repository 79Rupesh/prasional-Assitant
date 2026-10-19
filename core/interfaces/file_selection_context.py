from abc import ABC, abstractmethod


class FileSelectionContextProvider(ABC):

    @abstractmethod
    def set_results(self, results: list):
        pass

    @abstractmethod
    def get_results(self) -> list:
        pass

    @abstractmethod
    def clear(self):
        pass