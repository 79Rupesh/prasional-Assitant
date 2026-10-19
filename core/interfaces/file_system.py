from abc import ABC, abstractmethod


class FileSystemProvider(ABC):

    @abstractmethod
    def find(self, name: str) -> list:
        """Find files or folders by name."""
        pass

    @abstractmethod
    def list_directory(self, path: str) -> list:
        """List contents of a directory."""
        pass

    @abstractmethod
    def open(self, path: str) -> str:
        """Open a file or folder."""
        pass

    @abstractmethod
    def get_info(self, path: str) -> dict:
        """Return information about a file or folder."""
        pass