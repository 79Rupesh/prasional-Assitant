from abc import ABC, abstractmethod


class AppControllerProvider(ABC):

    @abstractmethod
    def open(self, app_name: str) -> str:
        """Open an application."""
        pass

    @abstractmethod
    def close(self, app_name: str) -> str:
        """Close an application."""
        pass