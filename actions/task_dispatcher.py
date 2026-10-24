import time
import tempfile
import os

from core.interfaces.task_dispatcher import TaskDispatcherProvider
from core.security.permission_manager import PermissionManager

from actions.search.web_search import WebSearchAction
from actions.file_system.windows_file_system import WindowsFileSystem
from actions.computer.windows_app_controller import WindowsAppController
from actions.browser.windows_browser import WindowsBrowserController
from actions.youtube.windows_youtube import WindowsYouTubeController

from brain.task.file_task_parser import FileTaskParser
from actions.file_system.windows_file_target_resolver import WindowsFileTargetResolver

from brain.task.file_selection_context import FileSelectionContext
from brain.task.file_selection_parser import FileSelectionParser

from brain.task.app_task_parser import AppTaskParser
from brain.task.browser_task_parser import BrowserTaskParser
from brain.task.youtube_task_parser import YouTubeTaskParser

from core.security.confirmation_manager import ConfirmationManager
from core.security.security_policy import SecurityPolicy

from actions.computer.computer_controller import ComputerController

from urllib.parse import quote_plus

from brain.task.youtube_video_resolver import YouTubeVideoResolver
from screen.screen_analyzer import ScreenAnalyzer
from screen.windows_screen import WindowsScreen

from brain.conversation.context import ConversationContext
from core.task_state import TaskStateManager

# from actions.computer.keyboard_action import KeyboardAction
# from actions.computer.mouse_action import MouseAction


class TaskDispatcher(TaskDispatcherProvider):

    def __init__(self, context=None):
        self.context = context or ConversationContext()
        
        self.permission_manager = PermissionManager()

        self.web_search = WebSearchAction()
        self.file_system = WindowsFileSystem()
        self.app_controller = WindowsAppController()
        self.browser_controller = WindowsBrowserController()
        self.youtube_controller = WindowsYouTubeController()

        self.file_parser = FileTaskParser()
        self.file_resolver = WindowsFileTargetResolver()

        self.file_selection_context = FileSelectionContext()
        self.file_selection_parser = FileSelectionParser()

        self.app_parser = AppTaskParser()
        self.browser_parser = BrowserTaskParser()
        self.youtube_parser = YouTubeTaskParser()

        self.confirmation_manager = ConfirmationManager()
        self.security_policy = SecurityPolicy()

        self.computer_controller = ComputerController()
        self.task_state = TaskStateManager()

        self.youtube_screen = WindowsScreen()
        self.youtube_resolver = YouTubeVideoResolver(
            ScreenAnalyzer()
)

        # self.keyboard_action = KeyboardAction()
        # self.mouse_action = MouseAction()

    def dispatch(self, task_type: str, text: str) -> str:
        """Run one task and retain truthful, session-only execution status."""
        task = self.task_state.start(task_type, text)
        try:
            result = self._dispatch(task_type, text)
        except Exception as error:
            self.task_state.fail(task, error)
            raise
        self.task_state.finish(task, result)
        return result

    def _dispatch(self, task_type: str, text: str) -> str:

        # Handle pending confirmation
        if self.confirmation_manager.has_pending():

            text_lower = text.lower().strip().rstrip(".!?")

            if text_lower in ["yes", "yeah", "yep", "confirm", "do it"]:

                pending = self.confirmation_manager.get_pending()

                action = pending["action"]
                target = pending["target"]

                self.confirmation_manager.confirm()

                if action == "delete":
                    return self.file_system.delete(target)

                if action == "rename":
                    source, destination = target.split(" to ", 1)

                    return self.file_system.rename(
                        source,
                        destination
                    )

                if action == "move":
                    source, destination = target.split(" to ", 1)

                    return self.file_system.move(
                        source,
                        destination
                    )

                return "Unknown confirmed action."

            if text_lower in ["no", "nope", "cancel", "don't"]:

                self.confirmation_manager.cancel()

                return "Okay, cancelled."

            return "Please say yes or no."

        selection = self.file_selection_parser.parse(text)

        if selection is not None:

            results = self.file_selection_context.get_results()

            if results:

                if selection < 1 or selection > len(results):
                    return (
                        f"Invalid selection. Please choose a number "
                        f"between 1 and {len(results)}."
                    )

                selected_path = results[selection - 1]

                action = self.file_selection_context.get_action()
                source = self.file_selection_context.get_source()

                self.file_selection_context.clear()

                if action == "move":

                    if self.security_policy.requires_confirmation("move"):

                        return self.confirmation_manager.request_confirmation(
                            "move",
                            f"{source} to {selected_path}"
                        )

                    return self.file_system.move(
                        source,
                        selected_path
                    )

                return self.file_system.open(selected_path)

        if task_type == "conversation":
            return "conversation"

        if not self.permission_manager.is_allowed(task_type):
            return f"Permission denied for {task_type}."

        if task_type == "computer_task":
            return self.handle_computer_task(text)

        if task_type == "browser_task":
            return self.handle_browser_task(text)

        if task_type == "web_task":
            return self.handle_web_task(text)

        if task_type == "youtube_task":
            return self.handle_youtube_task(text)

        if task_type == "file_task":
            return self.handle_file_task(text)

        return "Unknown task type."

    def handle_computer_task(self, text: str) -> str:

        text_lower = text.lower().strip()

        # Keyboard: type
        if text_lower.startswith("type "):
            value = text[5:].strip()

            if not value:
                return "No text specified."

            return self.computer_controller.type_text(value)

        # Keyboard: press
        if text_lower.startswith("press "):
            key = text_lower.replace("press ", "", 1).strip()

            if not key:
                return "No key specified."

            return self.computer_controller.press(key)

        # Keyboard: hotkey
        if text_lower.startswith("hotkey "):
            keys_text = text_lower.replace("hotkey ", "", 1).strip()

            if not keys_text:
                return "No keys specified."

            keys = [key.strip() for key in keys_text.split("+")]

            if not all(keys):
                return "Invalid hotkey."

            return self.computer_controller.hotkey(*keys)

        # Mouse: move
        if text_lower.startswith("move mouse to "):
            coordinates = text_lower.replace(
                "move mouse to ", "", 1
            ).strip()

            parts = coordinates.split()

            if len(parts) != 2:
                return "Invalid mouse coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "Invalid mouse coordinates."

            return self.computer_controller.move_mouse(x, y)

        # Mouse: click
        if text_lower.startswith("click at "):
            coordinates = text_lower.replace(
                "click at ", "", 1
            ).strip()

            parts = coordinates.split()

            if len(parts) != 2:
                return "Invalid mouse coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "Invalid mouse coordinates."

            return self.computer_controller.click(x, y)

        # Mouse: double click
        if text_lower.startswith("double click at "):
            coordinates = text_lower.replace(
                "double click at ", "", 1
            ).strip()

            parts = coordinates.split()

            if len(parts) != 2:
                return "Invalid mouse coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "Invalid mouse coordinates."

            return self.computer_controller.double_click(x, y)

        # Mouse: scroll
        if text_lower.startswith("scroll "):
            amount = text_lower.replace(
                "scroll ", "", 1
            ).strip()

            try:
                amount = int(amount)
            except ValueError:
                return "Invalid scroll amount."

            return self.computer_controller.scroll(amount)

       # Mouse: click on detected text
       # Mouse: click on detected text
        # Mouse: click on detected text
        if (
            text_lower.startswith("click on ")
            or text_lower.startswith("click ")
        ):
            if text_lower.startswith("click on "):
                target = text[9:].strip()
            else:
                target = text[6:].strip()


            # Use previously resolved UI target
            if target.lower() in ["it", "this", "that"]:
                ui_target = self.context.get_ui_target()

                if not ui_target or not ui_target["name"]:
                    return "I don't have a previous UI target."

                # If previous target has a destination URL,
                if ui_target["x"] is None or ui_target["y"] is None:
                    return "I don't have a valid previous UI target."

                return self.computer_controller.click_previous_target(
                    ui_target["name"],
                    ui_target["x"],
                    ui_target["y"]
                )

            if not target:
                return "No screen target specified."

            # Resolve target on current screen
            result = self.computer_controller.find_text_on_screen(target)

            if result["status"] != "success":
                return f"Unable to find '{target}' on screen."

            # Click resolved coordinates
            click_result = self.computer_controller.click(
                result["x"],
                result["y"]
            )

            self.context.set_ui_target(
                result["text"],
                target,
                result["x"],
                result["y"]
            )

            return click_result

        # Mouse: double click on detected text
        if text_lower.startswith("double click on "):
            target = text[16:].strip()

            if target.lower() in ["it", "this", "that"]:
                ui_target = self.context.get_ui_target()

                if not ui_target or not ui_target["name"]:
                    return "I don't have a previous UI target."

                target = ui_target["name"]

            if not target:
                return "No screen target specified."

            return self.computer_controller.double_click_text(target)

        # Mouse: move to detected text
        if text_lower.startswith("move to "):
            target = text[8:].strip()

            if target.lower() in ["it", "this", "that"]:
                ui_target = self.context.get_ui_target()

                if not ui_target or not ui_target["name"]:
                    return "I don't have a previous UI target."

                target = ui_target["name"]

            if not target:
                return "No screen target specified."

            return self.computer_controller.move_to_text(target)

        # Screen tasks
        if any(phrase in text_lower for phrase in [
            "take screenshot",
            "take a screenshot",
            "capture screen",
            "screenshot"
        ]):
            return self.computer_controller.capture_screen(
                "/tmp/ela_screenshot.png"
            )

        # App tasks
        parsed = self.app_parser.parse(text)

        operation = parsed["operation"]
        target = parsed["target"]

        if operation == "unknown":
            return "I don't know how to perform that computer task yet."

        if not target:
            return "No application specified."

        if operation == "open":
            return self.computer_controller.open_app(target)

        if operation == "close":
            return self.computer_controller.close_app(target)

        return "Unknown computer operation."

    def handle_browser_task(self, text: str) -> str:

        parsed = self.browser_parser.parse(text)

        operation = parsed["operation"]
        browser = parsed["browser"]
        query = parsed["query"]

        if operation == "unknown":
            return "I don't know how to perform that browser task yet."

        if operation == "open":
            if query:
                if not browser:
                    browser_context = self.context.get_browser_context()
                    if browser_context["browser"]:
                        browser = browser_context["browser"]

                result = self.browser_controller.open(
                    query,
                    browser
                )

                if result.startswith("Requested "):
                    self.context.set_browser_context(browser, None)

                return result

            if browser:
                app_name = self.browser_controller.resolver.resolve(browser)

                if not app_name:
                    return (
                        f"I couldn't find a supported browser "
                        f"named {browser}."
                    )

                result = self.browser_controller.open(
                    "about:blank",
                    browser
                )

                if result.startswith("Requested "):
                    self.context.set_browser_context(browser, None)

                return result

            return "Please specify a browser."

        if operation == "search":

            if not query:
                return "Please specify what you want me to search for."

            if not browser:
                browser_context = self.context.get_browser_context()

                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.search(
                query,
                browser
            )

            if result.startswith("Requested "):
                self.context.set_browser_context(browser, None)

            return result
        

        if operation == "close":

            if not browser:
                browser_context = self.context.get_browser_context()

                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.close(browser)

            self.context.set_browser_context(None, None)

            return result

        if operation == "back":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.back(browser)
            return result

        if operation == "forward":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.forward(browser)
            return result

        if operation == "refresh":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.refresh(browser)
            return result

        if operation == "new_tab":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.new_tab(browser)
            return result

        if operation == "close_tab":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.close_tab(browser)
            return result

        if operation == "next_tab":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.next_tab(browser)
            return result

        if operation == "previous_tab":
            if not browser:
                browser_context = self.context.get_browser_context()
                if browser_context["browser"]:
                    browser = browser_context["browser"]

            result = self.browser_controller.previous_tab(browser)
            return result
        
        return "Unknown browser operation."

    def handle_web_task(self, text: str) -> str:

        text_lower = text.lower().strip()

        prefixes = [
            "search for ",
            "search ",
            "google "
        ]

        for prefix in prefixes:

            if text_lower.startswith(prefix):

                query = text[len(prefix):].strip()
                query = query.rstrip(".!?")

                return self.web_search.execute(query)

        return self.web_search.execute(text)

    def handle_youtube_task(self, text: str) -> str:

        parsed = self.youtube_parser.parse(text)

        operation = parsed["operation"]
        query = parsed["query"]
        selection = parsed["selection"]
        index = parsed["index"]

        if operation == "unknown":
            return "I don't know how to perform that YouTube task yet."

        if operation == "open":
            return self.youtube_controller.open()

        if operation == "search":

            if not query:
                return "Please specify what you want to search for on YouTube."

            return self.youtube_controller.search(query)

        if operation == "play":

            # Normal query-based play
            if selection is None:

                if not query:
                    return "Please specify what you want me to play."

                return self.youtube_controller.play(query)

            # Screen-based video selection
            screenshot = os.path.join(
                tempfile.gettempdir(),
                "ela_youtube_live.png"
            )
            try:
                self.youtube_screen.capture(screenshot)
            except Exception as error:
                return f"I couldn't capture the screen: {error}"

            video = None

            if selection == "ordinal":
                video = self.youtube_resolver.resolve_ordinal(
                    screenshot,
                    index
                )

            elif selection == "title":
                video = self.youtube_resolver.resolve_title(
                    screenshot,
                    query
                )

            if not video:
                return "I couldn't find that video on the current YouTube screen."

            # OCR screenshot uses Retina pixels.
            # MouseController uses logical screen coordinates.
            x = int(
                (video["x"] + video["width"] // 2) / 2
            )

            y = int(
                (video["y"] + video["height"] // 2) / 2
            )

            result = self.computer_controller.click(x, y)

            if result:
                return f"Playing {video['title']}."

            return f"I found the video but couldn't click it."

        return "Unknown YouTube operation."

    def handle_file_task(self, text: str) -> str:

        parsed = self.file_parser.parse(text)

        operation = parsed["operation"]
        target = parsed["target"]

        if operation == "unknown":
            return "I don't know how to perform that file task yet."

        results = self.file_resolver.resolve(target)

        if not results:
            return f"I couldn't find anything named {target}."

        if operation == "find":

            if len(results) == 1:

                self.context.set_ui_target(
                    target,
                    results[0]
                )

                return f"Found: {results[0]}"

            self.context.set_ui_target(
                target,
                results[0]
            )

            return (
                f"I found {len(results)} matches for {target}. "
                f"First match: {results[0]}"
            )

        if operation == "open":

            if len(results) == 1:
                return self.file_system.open(results[0])

            displayed_results = results[:10]

            self.file_selection_context.set_results(
                displayed_results
            )

            lines = []

            for index, path in enumerate(
                displayed_results,
                start=1
            ):
                lines.append(f"{index}. {path}")

            return (
                f"I found {len(results)} matches for {target}.\n"
                + "\n".join(lines)
                + "\nWhich one should I open?"
            )

        if operation == "list":

            path = results[0]

            items = self.file_system.list_directory(path)

            if not items:
                return f"{target} is empty."

            preview = items[:10]

            return (
                f"{target} contains {len(items)} items: "
                + ", ".join(preview)
            )

        if operation == "info":

            info = self.file_system.get_info(results[0])

            if not info:
                return f"I couldn't get information about {target}."

            item_type = (
                "folder"
                if info["is_directory"]
                else "file"
            )

            return (
                f"{info['name']} is a {item_type}. "
                f"Path: {info['path']}. "
                f"Size: {info['size']} bytes."
            )

        if operation == "delete":

            if self.security_policy.requires_confirmation(operation):

                if not self.confirmation_manager.has_pending():

                    return self.confirmation_manager.request_confirmation(
                        "delete",
                        results[0]
                    )

                return "Deletion confirmation is pending."

            return self.file_system.delete(results[0])

        if operation == "rename":

            destination = parsed.get("destination")

            if not destination:
                return "Please specify the new name."

            if self.security_policy.requires_confirmation(operation):

                if not self.confirmation_manager.has_pending():

                    return self.confirmation_manager.request_confirmation(
                        "rename",
                        f"{results[0]} to {destination}"
                    )

                return "Rename confirmation is pending."

            return self.file_system.rename(
                results[0],
                destination
            )

        if operation == "move":

            destination = parsed.get("destination")

            if not destination:
                return "Please specify the destination."

            destination_results = self.file_resolver.resolve(
                destination,
                target_type="directory"
            )

            if not destination_results:
                return (
                    f"I couldn't find the destination "
                    f"{destination}."
                )

            if len(destination_results) > 1:

                displayed_results = destination_results[:10]

                self.file_selection_context.set_results(
                    displayed_results,
                    action="move",
                    source=results[0]
                )

                lines = []

                for index, path in enumerate(
                    displayed_results,
                    start=1
                ):
                    lines.append(f"{index}. {path}")

                return (
                    f"I found {len(destination_results)} possible "
                    f"destinations for {destination}.\n"
                    + "\n".join(lines)
                    + "\nWhich one should I use?"
                )

            selected_destination = destination_results[0]

            if self.security_policy.requires_confirmation(operation):

                if not self.confirmation_manager.has_pending():

                    return self.confirmation_manager.request_confirmation(
                        "move",
                        f"{results[0]} to {selected_destination}"
                    )

                return "Move confirmation is pending."

            return self.file_system.move(
                results[0],
                selected_destination
            )

        return "Unknown file operation."
