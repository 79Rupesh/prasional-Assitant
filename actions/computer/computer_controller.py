import tempfile
import os

from actions.computer.keyboard_action import KeyboardAction
from actions.computer.mouse_action import MouseAction
from screen.screen_controller import ScreenController
from screen.screen_analyzer import ScreenAnalyzer
from core.platform_support import create_app_controller, create_screen
from actions.computer.window_manager import WindowManager


class ComputerController:

    def __init__(self):
        self.keyboard = KeyboardAction()
        self.mouse = MouseAction()
        self.apps = create_app_controller()

        self.screen = ScreenController(create_screen())
        self.screen_analyzer = ScreenAnalyzer()
        self.window_manager = WindowManager()

    # Keyboard
    def type_text(self, text: str) -> str:
        return self.keyboard.execute(text)

    def press(self, key: str) -> str:
        return self.keyboard.press(key)

    def hotkey(self, *keys: str) -> str:
        return self.keyboard.hotkey(*keys)

    # Mouse
    def move_mouse(self, x: int, y: int) -> str:
        return self.mouse.move(x, y)

    def click(self, x: int, y: int) -> str:
        return self.mouse.click(x, y)

    def double_click(self, x: int, y: int) -> str:
        return self.mouse.double_click(x, y)

    def scroll(self, amount: int) -> str:
        return self.mouse.scroll(amount)

    # Applications
    def open_app(self, app_name: str) -> str:
        result = self.apps.open(app_name)
        if result.lower().startswith("opened ") and self.window_manager.snap_active_left():
            return result + " Placed on the left half of the screen."
        return result

    def activate_app(self, app_name: str) -> str:
        return self.apps.activate(app_name)

    def close_app(self, app_name: str) -> str:
        return self.apps.close(app_name)

    # Screen
    def capture_screen(self, output_path: str) -> str:
        return self.screen.capture(output_path)

    def find_text_on_screen(self, target: str) -> dict:
        screenshot_path = os.path.join(tempfile.gettempdir(), "ela_screen_analysis.png")

        self.screen.capture(screenshot_path)

        return self.screen_analyzer.find_text(
            screenshot_path,
            target
        )

    def move_to_text(self, target: str) -> str:
        result = self.find_text_on_screen(target)

        if result["status"] != "success":
            return f"Unable to find '{target}' on screen."

        x = result["x"]
        y = result["y"]

        self.move_mouse(x, y)

        return f"Moved mouse to '{result['text']}' at {x}, {y}"

    def click_text(self, target: str) -> str:
        result = self.find_text_on_screen(target)

        if result["status"] != "success":
            return f"Unable to find '{target}' on screen."

        x = result["x"]
        y = result["y"]

        self.click(x, y)

        return f"Clicked '{result['text']}' at {x}, {y}"

    def click_previous_target(self, target: str, x: int, y: int) -> str:
        screenshot_path = os.path.join(tempfile.gettempdir(), "ela_context_check.png")

        self.screen.capture(screenshot_path)

        result = self.screen_analyzer.analyze(screenshot_path)

        if result["status"] != "success":
            return "Unable to verify previous UI target."

        target_lower = target.lower().strip()

        for element in result["elements"]:
            text = element["text"].lower().strip()

            if text != target_lower:
                continue

            center_x = (
                element["pixel_x"]
                + element["pixel_width"] // 2
            )

            center_y = (
                element["pixel_y"]
                + element["pixel_height"] // 2
            )

            mouse_x = int(center_x * self.screen_analyzer.MOUSE_SCALE_X)
            mouse_y = int(center_y * self.screen_analyzer.MOUSE_SCALE_Y)

            distance = (
                (mouse_x - x) ** 2
                + (mouse_y - y) ** 2
            ) ** 0.5

            if distance <= 80:
                self.click(mouse_x, mouse_y)

                return (
                    f"Clicked previous target '{element['text']}' "
                    f"at {mouse_x}, {mouse_y}"
                )

        return f"Previous target '{target}' is no longer at the expected location."

    def double_click_text(self, target: str) -> str:
        result = self.find_text_on_screen(target)

        if result["status"] != "success":
            return f"Unable to find '{target}' on screen."

        x = result["x"]
        y = result["y"]

        self.double_click(x, y)

        return f"Double clicked '{result['text']}' at {x}, {y}"
