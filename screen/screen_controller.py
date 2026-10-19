from screen.screen_provider import ScreenProvider


class ScreenController:

    def __init__(self, screen: ScreenProvider):
        self.screen = screen

    def capture(self, output_path: str) -> str:
        return self.screen.capture(output_path)