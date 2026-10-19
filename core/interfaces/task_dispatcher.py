from abc import ABC, abstractmethod


class TaskDispatcherProvider(ABC):

    @abstractmethod
    def dispatch(self, task_type: str, text: str) -> str:
        """Dispatch a classified task to the appropriate tool."""
        pass