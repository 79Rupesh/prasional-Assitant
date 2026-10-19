import time

from screen.screen_analyzer import ScreenAnalyzer
from input.mac_mouse import MacMouse
from input.mouse_controller import MouseController


def main():
    analyzer = ScreenAnalyzer()
    mouse = MouseController(MacMouse())

    image_path = "/tmp/ela_screenshot.png"

    result = analyzer.find_text(
        image_path,
        "Explorer"
    )

    print("find_text result:")
    print(result)

    if result["status"] != "success":
        print("Text not found.")
        return

    x = result["x"]
    y = result["y"]

    print(f"Moving mouse to: {x}, {y}")

    mouse.move(x, y)

    time.sleep(2)

    print("Done.")


if __name__ == "__main__":
    main()