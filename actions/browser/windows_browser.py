import time
import webbrowser
from urllib.parse import quote_plus
from core.interfaces.browser.browser_controller import BrowserControllerProvider
from actions.browser.browser_resolver import BrowserResolver

class WindowsBrowserController(BrowserControllerProvider):
    def __init__(self):
        self.resolver = BrowserResolver()
        
    def open(self, url: str, browser: str = None) -> str:
        """Open a URL in the requested browser; Chrome is the default on Windows."""
        import os
        import subprocess
        import webbrowser

        url = (url or "").strip()
        if not url:
            return "No URL specified."

        if not url.startswith(("http://", "https://", "about:")):
            url = "https://" + url

        browser_name = (browser or "chrome").strip().lower()
        if browser_name in {"google chrome", "googlechrome"}:
            browser_name = "chrome"
        elif browser_name == "microsoft edge":
            browser_name = "edge"
        elif browser_name == "brave browser":
            browser_name = "brave"

        if browser_name in {"default", "system default"}:
            try:
                if webbrowser.open_new_tab(url):
                    return (
                        f"Requested {url} in the default browser; "
                        "page load could not be verified."
                    )
            except (webbrowser.Error, OSError):
                pass
            return "Unable to open the URL in the default browser."

        program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", "")

        executable_candidates = {
            "chrome": [
                os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(local_app_data, "Google", "Chrome", "Application", "chrome.exe"),
            ],
            "edge": [
                os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(program_files, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(local_app_data, "Microsoft", "Edge", "Application", "msedge.exe"),
            ],
            "firefox": [
                os.path.join(program_files, "Mozilla Firefox", "firefox.exe"),
                os.path.join(program_files_x86, "Mozilla Firefox", "firefox.exe"),
            ],
            "brave": [
                os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(program_files_x86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            ],
        }

        candidates = executable_candidates.get(browser_name, [])
        executable = next((path for path in candidates if path and os.path.isfile(path)), None)

        if executable:
            try:
                subprocess.Popen(
                    [executable, "--new-tab", url],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
                display_name = {
                    "chrome": "Google Chrome",
                    "edge": "Microsoft Edge",
                    "firefox": "Firefox",
                    "brave": "Brave Browser",
                }.get(browser_name, browser_name.title())
                return (
                    f"Requested {url} in {display_name}; "
                    "page load could not be verified."
                )
            except OSError as error:
                return f"Unable to launch {browser_name}: {error}"

        # Registered-browser fallback is allowed only for an explicitly requested
        # non-Chrome browser. Never silently redirect a Chrome request to Edge.
        if browser_name != "chrome":
            try:
                opened = webbrowser.get(browser_name).open_new_tab(url)
                if opened:
                    return (
                        f"Requested {url} in {browser_name.title()}; "
                        "page load could not be verified."
                    )
            except webbrowser.Error:
                pass

        if browser_name == "chrome":
            return "Google Chrome was not found in the usual installation folders."
        return f"Unable to find or launch the requested browser: {browser_name}."

    def search(self, query: str, browser: str = None) -> str:
        """Search Google in Chrome by default, regardless of Windows default browser."""
        from urllib.parse import quote_plus

        query = (query or "").strip()
        if not query:
            return "Please specify what you want to search for."

        url = "https://www.google.com/search?q=" + quote_plus(query)
        return self.open(url, browser or "chrome")

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
