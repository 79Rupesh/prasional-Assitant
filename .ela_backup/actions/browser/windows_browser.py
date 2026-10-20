import time
import webbrowser
from urllib.parse import quote_plus
from core.interfaces.browser.browser_controller import BrowserControllerProvider
from actions.browser.browser_resolver import BrowserResolver

class WindowsBrowserController(BrowserControllerProvider):
    def __init__(self):
        self.resolver = BrowserResolver()
        
    def open(self, url: str, browser: str = None) -> str:
        url = url.strip()
        if not url:
            return "No URL specified."
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            if browser:
                # Browser-specific executable paths vary; default browser is safest unless registered.
                webbrowser.get(browser).open_new_tab(url)
            else:
                webbrowser.open_new_tab(url)
            return f"Opened {url}."
        except webbrowser.Error:
            webbrowser.open_new_tab(url)
            return f"Opened {url} in the default browser."

    def search(self, query: str, browser: str = None) -> str:
        return self.open("https://www.google.com/search?q=" + quote_plus(query), browser)

    def _hotkey(self, *keys):
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return True
        except Exception:
            return False

    def close(self) -> str:
        return "Browser closing is not supported without selecting a specific window."
    def back(self, browser: str = None) -> str:
        return "Navigated back." if self._hotkey('alt', 'left') else "Unable to send browser shortcut."
    def forward(self, browser: str = None) -> str:
        return "Navigated forward." if self._hotkey('alt', 'right') else "Unable to send browser shortcut."
    def refresh(self, browser: str = None) -> str:
        return "Refreshed page." if self._hotkey('ctrl', 'r') else "Unable to send browser shortcut."
    def new_tab(self, browser: str = None) -> str:
        return "Opened a new tab." if self._hotkey('ctrl', 't') else "Unable to send browser shortcut."
    def close_tab(self, browser: str = None) -> str:
        return "Closed current tab." if self._hotkey('ctrl', 'w') else "Unable to send browser shortcut."
    def next_tab(self, browser: str = None) -> str:
        return "Switched to next tab." if self._hotkey('ctrl', 'tab') else "Unable to send browser shortcut."
    def previous_tab(self, browser: str = None) -> str:
        return "Switched to previous tab." if self._hotkey('ctrl', 'shift', 'tab') else "Unable to send browser shortcut."
    def wait_for_page(self, seconds: float = 2.0) -> str:
        time.sleep(max(0.0, min(float(seconds), 15.0)))
        return "Wait completed."
