from core.interfaces.action import Action
from input.windows_keyboard import WindowsKeyboard
from input.keyboard_controller import KeyboardController


class KeyboardAction(Action):

    def __init__(self):
        self.keyboard = KeyboardController(WindowsKeyboard())

    def execute(self, value: str) -> str:

        text = value.strip()

        if not text:
            return "No text specified."

        self.keyboard.type_text(text)

        return f"Typed {text}"

    def press(self, key: str) -> str:
        key = key.strip()

        if not key:
            return "No key specified."

        self.keyboard.press(key)

        return f"Pressed {key}"
    
    def hotkey(self, *keys: str) -> str:
        if not keys:
            return "No keys specified."

        self.keyboard.hotkey(*keys)

        return f"Pressed hotkey: {'+'.join(keys)}"