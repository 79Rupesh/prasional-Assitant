import re

from core.interfaces.task_classifier import TaskClassifierProvider
from brain.task.browser_task_parser import BrowserTaskParser
from brain.task.youtube_task_parser import YouTubeTaskParser


class LocalTaskClassifier(TaskClassifierProvider):
    def __init__(self):
        self.browser_parser = BrowserTaskParser()
        self.youtube_parser = YouTubeTaskParser()

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

        # Route only parsed, explicit navigation/search/play requests. Mentioning
        # a browser or website in ordinary conversation is not an action.
        if self.youtube_parser.parse(text).get("operation") != "unknown":
            return "youtube_task"

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
