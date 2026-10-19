from core.interfaces.dispatcher import ActionDispatcher
from actions.computer.open_app import OpenAppAction
from actions.search.web_search import WebSearchAction
from core.security.permission_manager import PermissionManager

class BasicActionDispatcher(ActionDispatcher):

    def __init__(self):
        self.open_app_action = OpenAppAction()
        self.search_action = WebSearchAction()
        self.permission_manager = PermissionManager()

        from actions.computer.keyboard_action import KeyboardAction
        from actions.computer.mouse_action import MouseAction

        self.keyboard_action = KeyboardAction()
        self.mouse_action = MouseAction()

    def dispatch(self, intent: str, text: str) -> str:


        if intent == "conversation":
            return "conversation"

        if not self.permission_manager.is_allowed(intent):
            return f"Permission denied for {intent}"



        if intent == "computer_action":
            return self.handle_computer_action(text)

        if intent == "web_search":
            return self.search_action.execute(self.extract_search_query(text))

        if intent == "phone_action":
            return "phone_action"

        return "unknown"

    def handle_computer_action(self, text: str) -> str:

        text_lower = text.lower().strip()

        if text_lower.startswith("open "):
            app_name = text_lower.replace("open ", "", 1).strip()
            app_name = app_name.rstrip(".!?")
            app_name = app_name.strip().title()

       

            return self.open_app_action.execute(app_name)

        if text_lower.startswith("move mouse to "):
            coordinates = text_lower.replace("move mouse to ", "", 1).strip()
            parts = coordinates.split()

            if len(parts) != 2:
                return "Invalid mouse coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "Invalid mouse coordinates."

            return self.mouse_action.move(x, y)

        if text_lower.startswith("click at "):
            coordinates = text_lower.replace("click at ", "", 1).strip()
            parts = coordinates.split()

            if len(parts) != 2:
                return "Invalid mouse coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "Invalid mouse coordinates."

            return self.mouse_action.click(x, y)

        if text_lower.startswith("double click at "):
            coordinates = text_lower.replace("double click at ", "", 1).strip()
            parts = coordinates.split()

            if len(parts) != 2:
                return "Invalid mouse coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "Invalid mouse coordinates."

            return self.mouse_action.double_click(x, y)

        if text_lower.startswith("scroll "):
            amount = text_lower.replace("scroll ", "", 1).strip()

            try:
                amount = int(amount)
            except ValueError:
                return "Invalid scroll amount."

            return self.mouse_action.scroll(amount)
        
        if text_lower.startswith("type "):
            value = text[5:].strip()
            return self.keyboard_action.execute(value)

        if text_lower.startswith("press "):
            key = text_lower.replace("press ", "", 1).strip()

            if not key:
                return "No key specified."

            return self.keyboard_action.press(key)

        if text_lower.startswith("hotkey "):
            keys_text = text_lower.replace("hotkey ", "", 1).strip()

            if not keys_text:
                return "No keys specified."

            keys = [key.strip() for key in keys_text.split("+")]

            if not all(keys):
                return "Invalid hotkey."

            return self.keyboard_action.hotkey(*keys)
        

        return "I don't know how to perform that computer action yet."

    def extract_search_query(self, text: str) -> str:
        text_lower = text.lower().strip()

        prefixes = [
            "search for ",
            "search ",
            "google ",
            "find online ",
            "look up "
        ]

        for prefix in prefixes:
            if text_lower.startswith(prefix):
                return text[len(prefix):].strip().rstrip(".!?")

        return text.strip().rstrip(".!?")