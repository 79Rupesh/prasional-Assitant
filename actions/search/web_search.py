from core.interfaces.action import Action
from core.platform_support import create_browser_controller


class WebSearchAction(Action):
    """Open general web searches in the platform's supported browser."""

    def __init__(self, browser_controller=None):
        self.browser_controller = browser_controller or create_browser_controller()

    def execute(self, value: str) -> str:
        query = (value or "").strip()
        if not query:
            return "What should I search for?"

        return self.browser_controller.search(query, browser="chrome")
