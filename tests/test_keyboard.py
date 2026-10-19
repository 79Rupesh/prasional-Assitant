import time

from actions.computer.mac_app_controller import MacAppController
from input.mac_keyboard import MacKeyboard


def main():
    app = MacAppController()
    keyboard = MacKeyboard()

    app.activate("TextEdit")
    time.sleep(1)

    keyboard.type_text("SPECIAL KEY TEST")
    time.sleep(0.5)

    # Editing
    keyboard.press("delete")
    keyboard.press("backspace")
    keyboard.press("forward delete")

    # Navigation
    keyboard.press("home")
    keyboard.press("end")
    keyboard.press("left")
    keyboard.press("right")
    keyboard.press("up")
    keyboard.press("down")

    # Other special keys
    keyboard.press("tab")
    keyboard.press("escape")

    # Caps Lock
    keyboard.press("caps lock")
    keyboard.type_text("caps test")
    keyboard.press("caps lock")

    # Page navigation
    keyboard.press("page up")
    keyboard.press("page down")

    print("Full special-key test completed.")


if __name__ == "__main__":
    main()