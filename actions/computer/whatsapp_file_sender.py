"""Stage and send one WhatsApp document with two explicit approvals."""

import os
import tempfile
import time

from core.platform_support import current_platform


class WhatsAppFileSender:
    def __init__(self, computer_controller, app_controller):
        self.computer = computer_controller
        self.app_controller = app_controller
        self.pending = None

    def stage(self, path: str, recipient: str) -> str:
        path = os.path.abspath(os.path.expanduser(path))
        recipient = (recipient or "").strip()
        if not os.path.isfile(path):
            return f"I couldn't find that file: {path}"
        if not recipient:
            return "Please say the WhatsApp contact name or phone number."

        opened = self.computer.open_app("WhatsApp")
        if not opened.lower().startswith("opened "):
            return opened

        keyboard = self.computer.keyboard
        time.sleep(0.8)
        if current_platform() == "windows":
            keyboard.hotkey("ctrl", "alt", "n")
        else:
            keyboard.hotkey("command", "ctrl", "n")
        time.sleep(0.4)
        keyboard.execute(recipient)
        time.sleep(0.7)
        keyboard.press("enter")
        time.sleep(0.5)

        header = self._find_element(recipient, top_only=True)
        if header is None:
            keyboard.press("escape")
            return (
                f"I couldn't verify the WhatsApp chat for {recipient}. "
                "Nothing was sent. Check the contact name and try again."
            )

        if current_platform() == "windows":
            keyboard.hotkey("alt", "a")
        else:
            keyboard.hotkey("option", "a")
        time.sleep(0.3)
        document = self._find_element("document", exact=True)
        if document is None:
            keyboard.press("escape")
            return "I couldn't find WhatsApp's Document attachment option. Nothing was sent."
        self._click_element(document)
        time.sleep(0.7)

        if current_platform() == "windows":
            keyboard.hotkey("alt", "n")
            keyboard.execute(path)
            keyboard.press("enter")
        else:
            keyboard.hotkey("command", "shift", "g")
            time.sleep(0.2)
            keyboard.execute(path)
            keyboard.press("enter")
            time.sleep(0.3)
            keyboard.press("enter")
        time.sleep(0.8)

        filename = os.path.basename(path)
        if self._find_element(filename) is None:
            keyboard.press("escape")
            return (
                f"WhatsApp did not show {filename} in the attachment preview. "
                "Nothing was sent."
            )
        if self._find_element("send", lower_right=True, exact=True) is None:
            keyboard.press("escape")
            return "I couldn't verify the Send button. Nothing was sent."

        self.pending = {"path": path, "recipient": recipient}
        return (
            f"I verified {filename} in the WhatsApp chat for {recipient}. "
            "Say yes to send it, or no to cancel."
        )

    def send_confirmed(self) -> str:
        if not self.pending:
            return "There is no WhatsApp file ready to send."

        path = self.pending["path"]
        recipient = self.pending["recipient"]
        filename = os.path.basename(path)
        if not os.path.isfile(path):
            self.pending = None
            return f"The file no longer exists: {path}"
        if self._find_element(recipient, top_only=True) is None:
            self.pending = None
            return "The WhatsApp chat changed, so I did not send the file."
        if self._find_element(filename) is None:
            self.pending = None
            return "The attachment preview changed, so I did not send the file."
        button = self._find_element("send", lower_right=True, exact=True)
        if button is None:
            self.pending = None
            return "The Send button is no longer visible. I did not send the file."

        self._click_element(button)
        time.sleep(0.8)
        if self._find_element("send", lower_right=True, exact=True) is not None:
            self.pending = None
            return (
                "I clicked Send, but the WhatsApp preview is still open. "
                "Please check the chat before retrying."
            )
        self.pending = None
        return f"WhatsApp accepted {filename} for {recipient}. Delivery status is not available."

    def cancel(self) -> None:
        self.pending = None
        try:
            self.computer.keyboard.press("escape")
        except Exception:
            pass

    def _elements(self):
        screenshot = os.path.join(tempfile.gettempdir(), "ela_whatsapp_verify.png")
        try:
            self.computer.screen.capture(screenshot)
            result = self.computer.screen_analyzer.analyze(screenshot)
        except Exception as error:
            print(f"WhatsApp screen verification failed: {type(error).__name__}: {error}")
            return []
        if result.get("status") != "success":
            print("WhatsApp screen verification is unavailable:", result.get("message", "OCR failed"))
            return []
        return result.get("elements", [])

    def _find_element(self, target, top_only=False, lower_right=False, exact=False):
        target = (target or "").strip().casefold()
        if not target:
            return None
        elements = self._elements()
        analyzer = self.computer.screen_analyzer
        screen_width = analyzer.SCREEN_WIDTH
        screen_height = analyzer.SCREEN_HEIGHT
        matches = []
        for element in elements:
            text = str(element.get("text", "")).strip().casefold()
            if exact and text != target:
                continue
            if target != text and target not in text:
                continue
            x = int(element.get("pixel_x", 0))
            y = int(element.get("pixel_y", 0))
            if top_only and y > screen_height * 0.25:
                continue
            if lower_right and (x < screen_width * 0.20 or y < screen_height * 0.55):
                continue
            matches.append(element)
        return matches[0] if matches else None

    def _click_element(self, element):
        analyzer = self.computer.screen_analyzer
        x = int((element["pixel_x"] + element["pixel_width"] / 2) * analyzer.MOUSE_SCALE_X)
        y = int((element["pixel_y"] + element["pixel_height"] / 2) * analyzer.MOUSE_SCALE_Y)
        self.computer.click(x, y)
