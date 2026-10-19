import pyautogui
from input.mouse_provider import MouseProvider

class WindowsMouse(MouseProvider):
    def move(self, x: int, y: int) -> None: pyautogui.moveTo(x, y)
    def click(self, x: int, y: int) -> None: pyautogui.click(x, y)
    def double_click(self, x: int, y: int) -> None: pyautogui.doubleClick(x, y)
    def scroll(self, amount: int) -> None: pyautogui.scroll(amount)
