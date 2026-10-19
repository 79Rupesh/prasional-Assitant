from abc import ABC, abstractmethod


class KeyboardProvider(ABC):

    @abstractmethod
    def press(self, key: str) -> None:
        pass

    @abstractmethod
    def type_text(self, text: str) -> None:
        pass

    @abstractmethod
    def hotkey(self, *keys: str) -> None:
        pass