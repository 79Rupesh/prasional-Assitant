import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile

from actions.computer.mac_app_controller import MacAppController
from actions.computer.computer_controller import ComputerController
from actions.browser.mac_browser import MacBrowserController
from brain.task.app_alias_resolver import AppAliasResolver
from brain.task.local_classifier import LocalTaskClassifier


PASS = 0
FAIL = 0
SKIP = 0


def test(name, fn):
    global PASS, FAIL

    try:
        result = fn()

        if result is False:
            raise AssertionError("Returned False")

        PASS += 1
        print(f"[PASS] {name}")

    except Exception as e:
        FAIL += 1
        print(f"[FAIL] {name}")
        print(f"       {type(e).__name__}: {e}")


def skip(name, reason):
    global SKIP
    SKIP += 1
    print(f"[SKIP] {name}")
    print(f"       {reason}")


# ============================================================
# 1. APP ALIAS RESOLUTION
# ============================================================

def test_aliases():
    resolver = AppAliasResolver()

    assert resolver.resolve("Text Edit") == "TextEdit"
    assert resolver.resolve("TextEdit") == "TextEdit"
    assert resolver.resolve("text editor") == "TextEdit"

    assert resolver.resolve("VS Code") == "Visual Studio Code"
    assert resolver.resolve("Visual Studio Code") == "Visual Studio Code"
    assert resolver.resolve("vscode") == "Visual Studio Code"


# ============================================================
# 2. LOCAL TASK CLASSIFIER
# ============================================================

def test_classifier_apps():
    classifier = LocalTaskClassifier()

    assert classifier.classify("Open Calculator") == "computer_task"
    assert classifier.classify("Open Text Edit") == "computer_task"
    assert classifier.classify("Open VS Code") == "computer_task"
    assert classifier.classify("Close Calculator") == "computer_task"


def test_classifier_keyboard():
    classifier = LocalTaskClassifier()

    assert classifier.classify("Type hello") == "computer_task"
    assert classifier.classify("Press Enter") == "computer_task"
    assert classifier.classify("Hotkey Command A") == "computer_task"


def test_classifier_mouse():
    classifier = LocalTaskClassifier()

    assert classifier.classify("Move mouse to 500 500") == "computer_task"
    assert classifier.classify("Click at 500 500") == "computer_task"
    assert classifier.classify("Double click at 500 500") == "computer_task"


def test_classifier_screen():
    classifier = LocalTaskClassifier()

    assert classifier.classify("Take a screenshot") == "computer_task"


def test_classifier_browser():
    classifier = LocalTaskClassifier()

    assert classifier.classify("Next tab") == "browser_task"
    assert classifier.classify("Previous tab") == "browser_task"
    assert classifier.classify("Close tab") == "browser_task"
    assert classifier.classify("Go back") == "browser_task"


# ============================================================
# 3. COMPUTER CONTROLLER
# ============================================================

def test_app_open():
    controller = ComputerController()

    result = controller.open_app("Calculator")

    assert "Opened" in result


def test_app_alias_open():
    controller = ComputerController()

    result = controller.open_app("Text Edit")

    assert "Opened TextEdit" in result


def test_keyboard_type():
    controller = ComputerController()

    result = controller.type_text("Ela V2 Automated Test")

    assert "Typed" in result


def test_keyboard_enter():
    controller = ComputerController()

    result = controller.press("enter")

    assert "Pressed" in result


def test_keyboard_hotkey():
    controller = ComputerController()

    result = controller.hotkey("command", "a")

    assert "hotkey" in result.lower()


def test_mouse_move():
    controller = ComputerController()

    result = controller.move_mouse(500, 500)

    assert "500" in result


def test_mouse_click():
    controller = ComputerController()

    result = controller.click(500, 500)

    assert "Clicked" in result


def test_mouse_double_click():
    controller = ComputerController()

    result = controller.double_click(500, 500)

    assert "Double clicked" in result


def test_mouse_scroll():
    controller = ComputerController()

    result = controller.scroll(-3)

    assert "Scrolled" in result


# ============================================================
# 4. SCREEN
# ============================================================

def test_screenshot():
    controller = ComputerController()

    path = "/tmp/ela_v2_automated_test.png"

    result = controller.capture_screen(path)

    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    assert path in result


def test_ocr():
    controller = ComputerController()

    result = controller.find_text_on_screen("ELA TEST")

    # OCR result can vary depending on what's currently visible.
    # We only require a valid structured result.
    assert isinstance(result, dict)
    assert "status" in result


# ============================================================
# 5. BROWSER CONTROLLER
# ============================================================

def test_browser_detection():
    browser = MacBrowserController()

    result = browser.get_active_browser()

    # None is acceptable if another app is frontmost.
    assert result is None or isinstance(result, str)


def test_browser_address_bar():
    browser = MacBrowserController()

    result = browser.focus_address_bar()

    assert isinstance(result, str)


def test_browser_navigation_methods():
    browser = MacBrowserController()

    assert isinstance(browser.new_tab(), str)
    assert isinstance(browser.next_tab(), str)
    assert isinstance(browser.previous_tab(), str)
    assert isinstance(browser.back(), str)
    assert isinstance(browser.forward(), str)
    assert isinstance(browser.refresh(), str)


# ============================================================
# 6. APP CONTROLLER
# ============================================================

def test_close_app():
    controller = MacAppController()

    controller.open("Text Edit")

    result = controller.close("Text Edit")

    assert "Closed TextEdit" in result


# ============================================================
# RUN
# ============================================================

def run_all_tests():
    global PASS, FAIL, SKIP

    print()
    print("=" * 60)
    print("              ELA V2 AUTOMATED TEST")
    print("=" * 60)
    print()

    test("App alias resolution", test_aliases)

    test("Classifier - apps", test_classifier_apps)
    test("Classifier - keyboard", test_classifier_keyboard)
    test("Classifier - mouse", test_classifier_mouse)
    test("Classifier - screen", test_classifier_screen)
    test("Classifier - browser", test_classifier_browser)

    test("Computer - open Calculator", test_app_open)
    test("Computer - open Text Edit", test_app_alias_open)

    test("Keyboard - type", test_keyboard_type)
    test("Keyboard - enter", test_keyboard_enter)
    test("Keyboard - hotkey", test_keyboard_hotkey)

    test("Mouse - move", test_mouse_move)
    test("Mouse - click", test_mouse_click)
    test("Mouse - double click", test_mouse_double_click)
    test("Mouse - scroll", test_mouse_scroll)

    test("Screen - screenshot", test_screenshot)
    test("Screen - OCR", test_ocr)

    test("Browser - detection", test_browser_detection)
    test("Browser - address bar", test_browser_address_bar)
    test("Browser - navigation methods", test_browser_navigation_methods)

    test("App - close TextEdit", test_close_app)

    print()
    print("=" * 60)
    print("                    SUMMARY")
    print("=" * 60)
    print(f"PASS : {PASS}")
    print(f"FAIL : {FAIL}")
    print(f"SKIP : {SKIP}")
    print("=" * 60)

    if FAIL:
        return 1

    print("ELA V2 AUTOMATED TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_all_tests())
