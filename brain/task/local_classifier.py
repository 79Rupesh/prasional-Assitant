import re

from core.interfaces.task_classifier import TaskClassifierProvider
from brain.task.browser_task_parser import BrowserTaskParser


class LocalTaskClassifier(TaskClassifierProvider):
    def __init__(self):
        self.browser_parser = BrowserTaskParser()

    def classify(self, text: str) -> str:
        text_lower = (text or "").lower().strip()
        text_lower = re.sub(
            r"^(okay|ok|alright|right|please|can you|could you)\s+",
            "",
            text_lower,
        )
        text_clean = re.sub(r"[^\w\s./:-]", "", text_lower)
        words = text_clean.split()

        if not words:
            return "unknown"

        # Explicit browser names should be treated as browser commands first.
        browsers = (
            "google chrome", "microsoft edge", "brave browser",
            "chrome", "firefox", "safari", "edge", "brave",
        )
        if any(re.search(rf"\b{re.escape(browser)}\b", text_lower) for browser in browsers):
            return "browser_task"

        # Keep dedicated YouTube search/playback operations intact.
        if (
            "youtube" in words
            or (
                "video" in words
                and any(word in words for word in ("play", "open", "watch"))
            )
        ):
            return "youtube_task"

        # Generic websites (Facebook, GitHub, arbitrary domains, etc.) and web
        # searches are browser tasks so they use the Chrome controller.
        parsed_browser_task = self.browser_parser.parse(text)
        if parsed_browser_task.get("operation") != "unknown":
            return "browser_task"

        # Web-search fallback phrases that do not fit a browser parser command.
        if (
            any(word in words for word in ("search", "google"))
            or text_lower.startswith(("look up ", "find online ", "search the web for "))
        ):
            return "web_task"

        # Keyboard / screen commands.
        if text_lower.startswith(("type ", "press ", "hotkey ")):
            return "computer_task"

        if any(phrase in text_lower for phrase in (
            "take screenshot", "capture screen", "take a screenshot", "screenshot",
        )):
            return "computer_task"

        # UI mouse tasks.
        if (
            text_lower.startswith(("move mouse to ", "click at ", "double click at ", "scroll "))
            or "click on " in text_lower
            or "click " in text_lower
            or "double click on " in text_lower
            or "double click " in text_lower
            or "move to " in text_lower
            or "move mouse to " in text_lower
        ):
            return "computer_task"

        # Files and folders. Keep these ahead of the generic app-open fallback.
        if any(word in words for word in (
            "file", "folder", "directory", "find", "list", "show",
            "create", "make", "rename", "move", "delete", "remove",
        )):
            return "file_task"

        # Opening normal desktop applications should remain a computer task.
        if text_lower.startswith(("open ", "launch ", "start ")):
            return "computer_task"

        if any(word in words for word in (
            "close", "launch", "click", "double", "type", "press",
            "hotkey", "scroll", "move",
        )):
            return "computer_task"

        return "conversation"
