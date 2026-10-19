import os
import subprocess
from core.interfaces.app_controller import AppControllerProvider
from actions.computer.windows_app_discovery import WindowsAppDiscovery
from brain.task.app_alias_resolver import AppAliasResolver

class WindowsAppController(AppControllerProvider):
    def __init__(self):
        self.discovery = WindowsAppDiscovery()
        self.alias_resolver = AppAliasResolver()

    def open(self, app_name: str) -> str:
        name = app_name.strip()
        if not name:
            return "No application specified."
        resolved = self.alias_resolver.resolve(name)
        target = self.discovery.find(resolved)
        if not target:
            return f"Unable to find {resolved}."
        try:
            if os.path.exists(target):
                os.startfile(target)
            else:
                subprocess.Popen([target], shell=False)
            return f"Opened {resolved}."
        except (OSError, subprocess.SubprocessError) as error:
            return f"Unable to open {resolved}: {error}"

    def activate(self, app_name: str) -> str:
        # Windows can launch/activate many apps by re-running their executable;
        # precise window activation is intentionally not claimed here.
        return self.open(app_name)

    def close(self, app_name: str) -> str:
        name = app_name.strip()
        if not name:
            return "No application specified."
        aliases = {"chrome": "chrome.exe", "google chrome": "chrome.exe", "edge": "msedge.exe", "microsoft edge": "msedge.exe", "notepad": "notepad.exe", "calculator": "CalculatorApp.exe", "firefox": "firefox.exe"}
        process = aliases.get(name.lower(), name if name.lower().endswith('.exe') else name + '.exe')
        try:
            result = subprocess.run(["taskkill", "/IM", process, "/T", "/F"], capture_output=True, text=True)
            if result.returncode == 0:
                return f"Closed {name}."
            return f"Unable to close {name}: {result.stderr.strip() or result.stdout.strip()}"
        except OSError as error:
            return f"Unable to close {name}: {error}"
