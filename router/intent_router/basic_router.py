from core.interfaces.router import IntentRouter


class BasicIntentRouter(IntentRouter):

    def route(self, text: str) -> str:
        text = text.lower().strip()

        if any(word in text for word in [
            "open",
            "close",
            "click",
            "type",
            "press",
            "launch"
        ]):
            return "computer_action"

        if any(word in text for word in [
            "search",
            "google",
            "find online",
            "look up"
        ]):
            return "web_search"

        if any(word in text for word in [
            "call",
            "phone",
            "dial"
        ]):
            return "phone_action"

        return "conversation"