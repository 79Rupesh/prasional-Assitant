from screen.screen_provider import ScreenProvider

class WindowsScreen(ScreenProvider):
    def capture(self, output_path: str) -> str:
        try:
            import pyautogui
        except ImportError as error:
            raise RuntimeError("Screen capture requires pyautogui. Install dependencies first.") from error
        image = pyautogui.screenshot()
        image.save(output_path)
        return output_path
