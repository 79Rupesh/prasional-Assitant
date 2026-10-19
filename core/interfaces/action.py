from abc import ABC, abstractmethod


class Action(ABC):

    @abstractmethod
    def execute(self, value: str) -> str:
        """Execute an action using a string input."""
        pass