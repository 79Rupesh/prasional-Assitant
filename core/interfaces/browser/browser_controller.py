from abc import ABC, abstractmethod


class BrowserControllerProvider(ABC):

    @abstractmethod
    def open(self, url: str) -> str:
        pass

    @abstractmethod
    def search(self, query: str) -> str:
        pass

    @abstractmethod
    def close(self) -> str:
        pass

    @abstractmethod
    def back(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def forward(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def refresh(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def new_tab(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def close_tab(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def next_tab(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def previous_tab(self, browser: str = None) -> str:
        pass

    @abstractmethod
    def wait_for_page(self, seconds: float = 2.0) -> str:
        pass