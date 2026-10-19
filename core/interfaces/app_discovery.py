from abc import ABC, abstractmethod


class AppDiscoveryProvider(ABC):

    @abstractmethod
    def find(self, app_name: str) -> str:
        """Find an installed application by name."""
        pass