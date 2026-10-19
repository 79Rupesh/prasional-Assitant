import subprocess
import time

from core.interfaces.browser.browser_controller import BrowserControllerProvider
from actions.browser.browser_resolver import BrowserResolver
from urllib.parse import quote_plus


class MacBrowserController(BrowserControllerProvider):

    def __init__(self):
        self.resolver = BrowserResolver()

    def get_active_browser(self):
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell
        return frontApp
        '''

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )

            active_app = result.stdout.strip()

            if active_app in {
                "Google Chrome",
                "Safari",
                "Microsoft Edge",
                "Brave Browser"
            }:
                return active_app

        except subprocess.CalledProcessError:
            return None

        return None

    def activate(self, browser: str) -> str:
        app_name = self.resolver.resolve(browser)

        if not app_name:
            return f"I couldn't find a supported browser named {browser}."

        script = f'''
        tell application "{app_name}"
            activate
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"{app_name} activated."

    def open(self, url: str, browser: str = None) -> str:
        app_name = self.resolver.resolve(browser) if browser else None

        if browser and not app_name:
            return f"I couldn't find a supported browser named {browser}."

        if not app_name:
            command = ["open", url]
            subprocess.run(command, check=False)
            return f"Opened {url} in the default browser."

        if app_name in [
            "Google Chrome",
            "Microsoft Edge",
            "Brave Browser",
            "Safari",
        ]:

            script = f'''
            tell application "{app_name}"
                activate
                if (count of windows) = 0 then
                    make new window
                end if
                set URL of active tab of front window to "{url}"
            end tell
            '''

            subprocess.run(
                ["osascript", "-e", script],
                check=False
            )

            return f"Opened {url} in {app_name}."

        command = ["open", "-a", app_name, url]
        subprocess.run(command, check=False)

        return f"Opened {url} in {app_name}."

    def search(self, query: str, browser: str = None) -> str:
        url = (
            "https://www.google.com/search?q="
            + quote_plus(query)
        )

        return self.open(url, browser)

    def close(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "{app_name}" to quit
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"{app_name} closed."

    def new_tab(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                keystroke "t" using command down
            end tell
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Opened a new tab in {app_name}."

    def close_tab(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                keystroke "w" using command down
            end tell
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Closed the current tab in {app_name}."

    def next_tab(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        if app_name == "Google Chrome":
            script = '''
            tell application "System Events"
                tell process "Google Chrome"
                    key code 124 using {command down, option down}
                end tell
            end tell
            '''
        elif app_name == "Safari":
            script = '''
            tell application "System Events"
                tell process "Safari"
                    keystroke "]" using {command down, shift down}
                end tell
            end tell
            '''
        else:
            return f"Next tab is not configured for {app_name}."

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Moved to the next tab in {app_name}."

    def previous_tab(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        if app_name == "Google Chrome":
            script = '''
            tell application "System Events"
                tell process "Google Chrome"
                    key code 123 using {command down, option down}
                end tell
            end tell
            '''
        elif app_name == "Safari":
            script = '''
            tell application "System Events"
                tell process "Safari"
                    keystroke "[" using {command down, shift down}
                end tell
            end tell
            '''
        else:
            return f"Previous tab is not configured for {app_name}."

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Moved to the previous tab in {app_name}."

    def wait_for_page(self, seconds: float = 2.0) -> str:
        time.sleep(seconds)
        return "Page ready."

    def back(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                keystroke "[" using command down
            end tell
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Went back in {app_name}."

    def forward(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                keystroke "]" using command down
            end tell
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Went forward in {app_name}."

    def refresh(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                keystroke "r" using command down
            end tell
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Refreshed {app_name}."


    def focus_address_bar(self, browser: str = None) -> str:

        if browser:
            app_name = self.resolver.resolve(browser)

            if not app_name:
                return f"I couldn't find a supported browser named {browser}."
        else:
            app_name = self.get_active_browser()

            if not app_name:
                return "I couldn't detect the active supported browser."

        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                keystroke "l" using command down
            end tell
        end tell
        '''

        subprocess.run(
            ["osascript", "-e", script],
            check=False
        )

        return f"Address bar focused in {app_name}."

    def get_current_url(self, browser: str = "Google Chrome") -> str:
        browser = browser.strip()

        script = ""

        if browser == "Google Chrome":
            script = '''
            tell application "Google Chrome"
                return URL of active tab of front window
            end tell
            '''

        elif browser == "Safari":
            script = '''
            tell application "Safari"
                return URL of front document
            end tell
            '''

        elif browser == "Microsoft Edge":
            script = '''
            tell application "Microsoft Edge"
                return URL of active tab of front window
            end tell
            '''

        elif browser == "Brave Browser":
            script = '''
            tell application "Brave Browser"
                return URL of active tab of front window
            end tell
            '''

        else:
            return ""

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout.strip()

        except subprocess.CalledProcessError:
            return ""

    def get_browser_urls(self):
        browsers = {
            "Google Chrome": '''
                tell application "Google Chrome"
                    if (count windows) > 0 then
                        return URL of active tab of front window
                    end if
                    return ""
                end tell
            ''',

            "Safari": '''
                tell application "Safari"
                    if (count windows) > 0 then
                        return URL of front document
                    end if
                    return ""
                end tell
            ''',

            "Microsoft Edge": '''
                tell application "Microsoft Edge"
                    if (count windows) > 0 then
                        return URL of active tab of front window
                    end if
                    return ""
                end tell
            ''',

            "Brave Browser": '''
                tell application "Brave Browser"
                    if (count windows) > 0 then
                        return URL of active tab of front window
                    end if
                    return ""
                end tell
            '''
        }

        result = {}

        for browser, script in browsers.items():
            try:
                process = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True,
                    check=True
                )

                result[browser] = process.stdout.strip()

            except subprocess.CalledProcessError:
                result[browser] = ""

        return result

    def detect_url_change(self, before_urls, after_urls):
        for browser in before_urls:
            before = before_urls.get(browser, "")
            after = after_urls.get(browser, "")

            if before and after and before != after:
                return browser, after

        return None, None