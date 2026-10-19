import subprocess

from core.interfaces.app_controller import AppControllerProvider
from actions.computer.mac_app_discovery import MacAppDiscovery
from brain.task.app_alias_resolver import AppAliasResolver


class MacAppController(AppControllerProvider):

    def __init__(self):
        self.discovery = MacAppDiscovery()
        self.alias_resolver = AppAliasResolver()

    def open(self, app_name: str) -> str:

        app_name = app_name.strip()

        if not app_name:
            return "No application specified."

        resolved_name = self.alias_resolver.resolve(app_name)

        app_path = self.discovery.find(resolved_name)

        if not app_path:
            return f"Unable to find {resolved_name}"

        try:
            subprocess.run(
                ["open", app_path],
                check=True
            )

            return f"Opened {resolved_name}"

        except subprocess.CalledProcessError:
            return f"Unable to open {resolved_name}"

    def activate(self, app_name: str) -> str:

        app_name = app_name.strip()

        if not app_name:
            return "No application specified."

        resolved_name = self.alias_resolver.resolve(app_name)

        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'tell application "{resolved_name}" to activate'
                ],
                check=True
            )

            return f"Activated {resolved_name}"

        except subprocess.CalledProcessError:
            return f"Unable to activate {resolved_name}"

    def close(self, app_name: str) -> str:

        app_name = app_name.strip()

        if not app_name:
            return "No application specified."

        resolved_name = self.alias_resolver.resolve(app_name)

        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'tell application "{resolved_name}" to quit'
                ],
                check=True
            )

            return f"Closed {resolved_name}"

        except subprocess.CalledProcessError:
            return f"Unable to close {resolved_name}"