from input.mouse_provider import MouseProvider


class MouseController:

    def __init__(self, mouse: MouseProvider):
        self.mouse = mouse

    def move(self, x: int, y: int) -> None:
        self.mouse.move(x, y)

    def click(self, x: int, y: int) -> None:
        self.mouse.click(x, y)

    def double_click(self, x: int, y: int) -> None:
        self.mouse.double_click(x, y)

    def scroll(self, amount: int) -> None:
        self.mouse.scroll(amount)