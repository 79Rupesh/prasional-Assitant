from abc import ABC, abstractmethod


class AppAliasResolverProvider(ABC):

    @abstractmethod
    def resolve(self, name: str) -> str:
        """Resolve a natural app alias to an application name."""
        pass