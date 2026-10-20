from core.interfaces.action import Action
from actions.browser.windows_browser import WindowsBrowserController


class WebSearchAction(Action):
    """Open general web searches in Google Chrome, not the Windows default browser."""

    def __init__(self):
        self.browser_controller = WindowsBrowserController()

    def execute(self, value: str) -> str:
        query = (value or "").strip()
        if not query:
            return "What should I search for?"

        return self.browser_controller.search(query, browser="chrome")
