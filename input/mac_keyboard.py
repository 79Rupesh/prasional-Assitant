import subprocess
import pyautogui

from input.keyboard_provider import KeyboardProvider


class MacKeyboard(KeyboardProvider):

    KEYCODES = {
        "delete": 51,
        "backspace": 51,
        "enter": 36,
        "return": 36,
        "tab": 48,
        "space": 49,
        "escape": 53,
        "esc": 53,
        "caps lock": 57,
        "capslock": 57,
        "left": 123,
        "right": 124,
        "down": 125,
        "up": 126,
        "forward delete": 117,
        "home": 115,
        "end": 119,
        "page up": 116,
        "page down": 121,
    }

    def press(self, key: str) -> None:
        key = key.strip().lower()

        aliases = {
            "cmd": "command",
            "ctrl": "control",
            "alt": "option",
            "esc": "escape",
            "capslock": "caps lock",
            "backspace": "backspace",
        }

        key = aliases.get(key, key)

        if key in self.KEYCODES:
            keycode = self.KEYCODES[key]

            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'tell application "System Events" to key code {keycode}'
                ],
                check=True
            )
            return

        pyautogui.press(key)

    def type_text(self, text: str) -> None:
        pyautogui.write(text)

    def hotkey(self, *keys: str) -> None:
        if len(keys) != 2:
            raise ValueError("Only 2-key hotkeys are supported.")

        modifier = keys[0].lower()
        key = keys[1].lower()

        modifier_map = {
            "command": "command down",
            "cmd": "command down",
            "shift": "shift down",
            "option": "option down",
            "alt": "option down",
            "control": "control down",
            "ctrl": "control down",
        }

        if modifier not in modifier_map:
            raise ValueError(f"Unsupported modifier: {modifier}")

        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to keystroke "{key}" using {modifier_map[modifier]}'
            ],
            check=True
        )