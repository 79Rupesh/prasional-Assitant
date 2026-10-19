from abc import ABC, abstractmethod


class MouseProvider(ABC):

    @abstractmethod
    def move(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def click(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def double_click(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def scroll(self, amount: int) -> None:
        pass