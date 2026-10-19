from core.interfaces.action import Action
from input.windows_mouse import WindowsMouse
from input.mouse_controller import MouseController


class MouseAction(Action):

    def __init__(self):
        self.mouse = MouseController(WindowsMouse())

    def execute(self, value: str) -> str:
        return "Mouse action ready."

    def move(self, x: int, y: int) -> str:
        self.mouse.move(x, y)
        return f"Moved mouse to {x}, {y}"

    def click(self, x: int, y: int) -> str:
        self.mouse.click(x, y)
        return f"Clicked at {x}, {y}"

    def double_click(self, x: int, y: int) -> str:
        self.mouse.double_click(x, y)
        return f"Double clicked at {x}, {y}"

    def scroll(self, amount: int) -> str:
        self.mouse.scroll(amount)
        return f"Scrolled {amount}"