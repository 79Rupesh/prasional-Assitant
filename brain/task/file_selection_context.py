from core.interfaces.file_selection_context import (
    FileSelectionContextProvider
)


class FileSelectionContext(FileSelectionContextProvider):

    def __init__(self):
        self.results = []
        self.action = None
        self.source = None

    def set_results(
        self,
        results: list,
        action: str = "open",
        source: str = None
    ):
        self.results = results
        self.action = action
        self.source = source

    def get_results(self) -> list:
        return self.results

    def get_action(self) -> str:
        return self.action

    def get_source(self) -> str:
        return self.source

    def clear(self):
        self.results.clear()
        self.action = None
        self.source = None