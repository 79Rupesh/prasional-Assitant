import re
from core.interfaces.task_classifier import TaskClassifierProvider


class LocalTaskClassifier(TaskClassifierProvider):

    def classify(self, text: str) -> str:

     

        text_lower = text.lower().strip()
        text_lower = re.sub(
            r"^(okay|ok|alright|right|please|can you|could you)\s+",
            "",
            text_lower
        )
        text_clean = re.sub(r"[^\w\s]", "", text_lower)
        words = text_clean.split()

        if not words:
            return "unknown"

        # Browser tasks
        browsers = [
            "chrome",
            "google chrome",
            "firefox",
            "safari",
            "edge",
            "microsoft edge",
            "brave",
            "brave browser",
        ]

        if any(browser in text_lower for browser in browsers):
            return "browser_task"

        
        # YouTube tasks
        if (
            "youtube" in words
            or (
                "video" in words
                and any(word in words for word in [
                    "play",
                    "open",
                    "watch"
                ])
            )
        ):
            return "youtube_task"

        # Browser navigation tasks
        if any(phrase in text_lower for phrase in [
            "previous tab",
            "next tab",
            "previous page",
            "back to the previous page",
            "go back",
            "move forward",
            "forward",
            "reload",
            "refresh",
            "new tab",
            "close tab",
            "close the tab",
            "close this tab",
        ]):
            return "browser_task"


        # Web tasks
        if any(word in words for word in [
            "search",
            "google"
        ]):
            return "web_task"

        # Keyboard tasks
        if (
            text_lower.startswith("type ")
            or text_lower.startswith("press ")
            or text_lower.startswith("hotkey ")
        ):
            return "computer_task"

        # Screen tasks
        if any(phrase in text_lower for phrase in [
            "take screenshot",
            "capture screen",
            "take a screenshot",
            "screenshot"
        ]):
            return "computer_task"

        
         # UI mouse tasks
        if (
            text_lower.startswith("move mouse to ")
            or text_lower.startswith("click at ")
            or text_lower.startswith("double click at ")
            or text_lower.startswith("scroll ")
            or "click on " in text_lower
            or "click " in text_lower
            or "double click on " in text_lower
            or "double click " in text_lower
            or "move to " in text_lower
            or "move mouse to " in text_lower
        ):
            return "computer_task"

        # App / Computer open tasks
        if text_lower.startswith("open "):
            return "computer_task"

        # File tasks
        if any(word in words for word in [
            "file",
            "folder",
            "directory",
            "find",
            "open",
            "list",
            "show",
            "create",
            "make",
            "rename",
            "move",
            "delete",
            "remove"
        ]):
            return "file_task"

        # Computer tasks
        if any(word in words for word in [
            
            "close",
            "launch",
            "click",
            "double",
            "type",
            "press",
            "hotkey",
            "scroll",
            "move"
        ]):
            return "computer_task"
        
        # Otherwise conversation
        return "conversation"