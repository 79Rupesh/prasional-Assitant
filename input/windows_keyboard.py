import pyautogui
from input.keyboard_provider import KeyboardProvider

class WindowsKeyboard(KeyboardProvider):
    ALIASES = {"cmd": "win", "command": "win", "option": "alt", "return": "enter", "esc": "escape", "del": "delete"}
    def press(self, key: str) -> None:
        key = key.strip().lower()
        key = self.ALIASES.get(key, key)
        pyautogui.press(key)
    def type_text(self, text: str) -> None:
        # pyautogui.write is reliable for ASCII; Unicode text uses clipboard paste on Windows.
        try:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
        except ImportError:
            pyautogui.write(text)
    def hotkey(self, *keys: str) -> None:
        if not keys:
            raise ValueError("At least one key is required.")
        normalized = [self.ALIASES.get(k.strip().lower(), k.strip().lower()) for k in keys]
        pyautogui.hotkey(*normalized)
