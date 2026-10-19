from abc import ABC, abstractmethod


class FileTargetResolverProvider(ABC):

    @abstractmethod
    def resolve(self, target: str) -> list:
        """Resolve a natural-language file target into filesystem paths."""
        pass