import os

from core.interfaces.action import Action
from core.platform_support import current_platform
from input.mac_keyboard import MacKeyboard
from input.windows_keyboard import WindowsKeyboard
from input.keyboard_controller import KeyboardController


class KeyboardAction(Action):

    def __init__(self):
        provider = WindowsKeyboard() if current_platform() == "windows" else MacKeyboard()
        self.keyboard = KeyboardController(provider)

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
