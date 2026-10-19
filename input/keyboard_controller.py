from input.keyboard_provider import KeyboardProvider


class KeyboardController:

    def __init__(self, keyboard: KeyboardProvider):
        self.keyboard = keyboard

    def press(self, key: str) -> None:
        self.keyboard.press(key)

    def type_text(self, text: str) -> None:
        self.keyboard.type_text(text)

    def hotkey(self, *keys: str) -> None:
        self.keyboard.hotkey(*keys)