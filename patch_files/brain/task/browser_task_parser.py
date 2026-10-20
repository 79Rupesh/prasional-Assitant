"""Parse common browser navigation and web-search voice commands."""

import re
from urllib.parse import quote_plus


class BrowserTaskParser:
    BROWSERS = {
        "google chrome": "chrome",
        "chrome": "chrome",
        "microsoft edge": "edge",
        "edge": "edge",
        "firefox": "firefox",
        "brave browser": "brave",
        "brave": "brave",
        "safari": "safari",
    }

    WEBSITE_ALIASES = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "google drive": "https://drive.google.com",
        "google maps": "https://maps.google.com",
        "chatgpt": "https://chatgpt.com",
        "openai": "https://openai.com",
        "claude": "https://claude.ai",
        "copilot": "https://copilot.microsoft.com",
        "x": "https://x.com",
        "twitter": "https://x.com",
        "whatsapp": "https://web.whatsapp.com",
        "whatsapp web": "https://web.whatsapp.com",
        "wikipedia": "https://www.wikipedia.org",
        "amazon": "https://www.amazon.in",
        "reddit": "https://www.reddit.com",
        "stackoverflow": "https://stackoverflow.com",
        "netflix": "https://www.netflix.com",
        "spotify": "https://open.spotify.com",
        "tiktok": "https://www.tiktok.com",
        "yahoo": "https://www.yahoo.com",
        "outlook": "https://outlook.live.com",
        "canva": "https://www.canva.com",
        "duckduckgo": "https://duckduckgo.com",
        "microsoft": "https://www.microsoft.com",
    }

    DESKTOP_APPS = {
        "calculator", "notepad", "paint", "file explorer", "explorer",
        "command prompt", "cmd", "terminal", "task manager", "settings",
        "control panel", "word", "microsoft word", "excel", "microsoft excel",
        "powerpoint", "visual studio code", "vs code", "vscode", "pycharm",
    }

    OPEN_PREFIXES = (
        "open ", "launch ", "start ", "visit ", "go to ",
        "navigate to ", "browse to ", "open website ",
        "open the website ", "open site ", "open the site ",
        "open webpage ", "open web page ",
    )

    def parse(self, text: str) -> dict:
        original = (text or "").strip()
        # Remove common wake-word lead-ins without altering query spelling.
        original = re.sub(
            r"^(?:(?:hey|hello|hi)\s+)?ela[\s,:-]+",
            "",
            original,
            flags=re.IGNORECASE,
        ).strip()
        original = original.rstrip(".!? ")
        lowered = original.lower().strip()

        # Correct common Whisper substitutions for tab commands.
        for wrong, right in (
            ("new table", "new tab"),
            ("next table", "next tab"),
            ("previous table", "previous tab"),
            ("close table", "close tab"),
        ):
            lowered = lowered.replace(wrong, right)

        browser = self._browser_in_text(lowered)

        # Browser navigation commands are checked before generic open/close.
        if lowered in {"back", "go back", "previous page", "go to previous page", "go to the previous page"}:
            return self._result("back", browser)

        if lowered in {"forward", "go forward", "next page", "go to next page", "go to the next page"}:
            return self._result("forward", browser)

        if lowered in {"new tab", "open new tab", "open a new tab", "open the new tab"}:
            return self._result("new_tab", browser or "chrome")

        if lowered in {"close tab", "close the tab", "close this tab", "close current tab", "close the current tab"}:
            return self._result("close_tab", browser)

        if lowered in {"next tab", "go to next tab", "go to the next tab"}:
            return self._result("next_tab", browser)

        if lowered in {"previous tab", "prev tab", "go to previous tab", "go to the previous tab"}:
            return self._result("previous_tab", browser)

        if lowered.startswith(("refresh", "reload")):
            return self._result("refresh", browser)

        # Search in Chrome by default. Browser suffixes are removed from the query.
        search_match = re.match(
            r"^(?:please\s+)?(?:search(?:\s+for)?|google|look\s+up|find\s+online)\s+(.+)$",
            original,
            flags=re.IGNORECASE,
        )
        if search_match:
            query = self._strip_browser_suffix(search_match.group(1)).strip(" .!?\t")
            if query:
                return {"operation": "search", "browser": browser or "chrome", "query": query}
            return {"operation": "search", "browser": browser or "chrome", "query": None}

        # Open a specific browser without a website.
        open_prefix, target = self._open_target(original)
        if open_prefix is not None:
            target = self._strip_browser_suffix(target).strip(" \t.,!?")
            target = re.sub(
                r"^(?:the\s+)?(?:website|site|web\s*page)\s+(?:(?:called|named)\s+)?",
                "",
                target,
                flags=re.IGNORECASE,
            ).strip()
            target_lower = target.lower().strip()

            if not target_lower:
                return self._result("unknown", browser)

            if target_lower in self.DESKTOP_APPS:
                # Let the computer-task handler open ordinary desktop applications.
                return self._result("unknown", browser)

            if target_lower in self.BROWSERS:
                return {"operation": "open", "browser": self.BROWSERS[target_lower], "query": None}

            # Known website name -> direct homepage.
            if target_lower in self.WEBSITE_ALIASES:
                return {
                    "operation": "open",
                    "browser": browser or "chrome",
                    "query": self.WEBSITE_ALIASES[target_lower],
                }

            # A URL/domain spoken directly by the user.
            if target_lower.startswith(("http://", "https://")):
                url = target
            elif target_lower.startswith("www."):
                url = "https://" + target
            elif self._looks_like_domain(target_lower):
                url = "https://" + target
            else:
                # If the site name is not a known alias, search for it rather than
                # constructing a potentially invalid URL such as https://my-site.
                url = "https://www.google.com/search?q=" + quote_plus(target)

            return {"operation": "open", "browser": browser or "chrome", "query": url}

        # Close/quit the browser, not just a tab.
        if lowered.startswith(("close browser", "quit browser", "exit browser", "close chrome", "quit chrome", "exit chrome")):
            return self._result("close", browser or "chrome")

        return self._result("unknown", browser)

    @staticmethod
    def _result(operation: str, browser: str = None) -> dict:
        return {"operation": operation, "browser": browser, "query": None}

    def _browser_in_text(self, lowered: str):
        for name in sorted(self.BROWSERS, key=len, reverse=True):
            if re.search(rf"\b{re.escape(name)}\b", lowered):
                return self.BROWSERS[name]
        return None

    def _open_target(self, original: str):
        lowered = original.lower().strip()
        # More specific prefixes precede shorter ones.
        for prefix in sorted(self.OPEN_PREFIXES, key=len, reverse=True):
            if lowered.startswith(prefix):
                return prefix, original[len(prefix):].strip()
        return None, None

    def _strip_browser_suffix(self, query: str) -> str:
        return re.sub(
            r"\s+(?:in|on|using|with)\s+(?:google\s+chrome|chrome|microsoft\s+edge|edge|firefox|brave(?:\s+browser)?|safari)\s*$",
            "",
            query,
            flags=re.IGNORECASE,
        )

    @staticmethod
    def _looks_like_domain(value: str) -> bool:
        if " " in value or not value:
            return False
        if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?", value):
            return True
        return bool(
            re.fullmatch(
                r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
                r"(?:com|org|net|io|ai|edu|gov|co|in|dev|app|tech|me|info|biz|uk|us|ca|au|jp|de|fr|xyz|online|site|com\.in)"
                r"(?::\d+)?(?:/[^\s]*)?",
                value,
                flags=re.IGNORECASE,
            )
        )
