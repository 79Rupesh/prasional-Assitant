
class BrowserTaskParser:

    def parse(self, text: str) -> dict:
        text_lower = text.lower().strip().rstrip(".!?")

        # Correct common speech-recognition mistakes
        corrections = {
            "new table": "new tab",
            "next table": "next tab",
            "previous table": "previous tab",
            "close table": "close tab",
        }
        for wrong, correct in corrections.items():
            text_lower = text_lower.replace(wrong, correct)

        # Normalize Hinglish commands
        for phrase in ("khol do", "kholo", "chalao"):
            text_lower = text_lower.replace(phrase, "open")

        for phrase in ("band kar do", "band karo"):
            text_lower = text_lower.replace(phrase, "close")

        text_lower = text_lower.replace("peeche jao", "go back")
        text_lower = text_lower.replace("aage jao", "go forward")
        text_lower = text_lower.replace("refresh karo", "refresh")

        # Support commands such as "Chrome open"
        browser_names = (
            "google chrome", "microsoft edge", "brave browser",
            "chrome", "firefox", "safari", "edge", "brave"
        )
        for name in browser_names:
            if text_lower == name + " open":
                text_lower = "open " + name
                break

        operation = "unknown"
        browser = None
        query = None

        browsers = {
            "google chrome": "chrome",
            "microsoft edge": "edge",
            "brave browser": "brave",
            "chrome": "chrome",
            "firefox": "firefox",
            "safari": "safari",
            "edge": "edge",
            "brave": "brave",
        }

        for name, value in browsers.items():
            if name in text_lower:
                browser = value
                break

        # Open a browser or website
        if text_lower.startswith(("open ", "launch ", "start ")):
            operation = "open"
            target = text_lower.split(" ", 1)[1].strip()

            if target in browser_names:
                query = None
            else:
                query = target or None

        elif text_lower in (
            "back", "go back", "previous page",
            "go to previous page", "go to the previous page"
        ):
            operation = "back"

        elif text_lower in (
            "forward", "go forward", "next page",
            "go to next page", "go to the next page"
        ):
            operation = "forward"

        elif text_lower in (
            "new tab", "open new tab", "open a new tab",
            "open the new tab"
        ):
            operation = "new_tab"

        elif text_lower in (
            "close tab", "close the tab", "close this tab",
            "close current tab", "close the current tab"
        ):
            operation = "close_tab"

        elif text_lower in (
            "next tab", "go to next tab", "go to the next tab"
        ):
            operation = "next_tab"

        elif text_lower in (
            "previous tab", "prev tab",
            "go to previous tab", "go to the previous tab"
        ):
            operation = "previous_tab"

        elif text_lower.startswith(("refresh", "reload")):
            operation = "refresh"

        elif text_lower.startswith(("close ", "quit ", "exit ")):
            operation = "close"

        elif text_lower.startswith(("search ", "google ")):
            operation = "search"
            for prefix in ("search for ", "search ", "google "):
                if text_lower.startswith(prefix):
                    query = text_lower[len(prefix):].strip()
                    break

        return {
            "operation": operation,
            "browser": browser,
            "query": query,
        }
