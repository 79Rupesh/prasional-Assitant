import os
import shutil
import subprocess
from core.interfaces.app_discovery import AppDiscoveryProvider

class WindowsAppDiscovery(AppDiscoveryProvider):
    def find(self, app_name: str) -> str:
        name = app_name.strip()
        if not name:
            return ""
        # Resolve common executable names and PATH-installed applications.
        aliases = {
            "chrome": "chrome.exe", "google chrome": "chrome.exe",
            "edge": "msedge.exe", "microsoft edge": "msedge.exe",
            "firefox": "firefox.exe", "notepad": "notepad.exe",
            "calculator": "calc.exe", "calc": "calc.exe",
            "explorer": "explorer.exe", "file explorer": "explorer.exe",
            "command prompt": "cmd.exe", "cmd": "cmd.exe",
            "powershell": "powershell.exe", "terminal": "wt.exe",
            "vscode": "code.exe", "visual studio code": "code.exe",
        }
        executable = aliases.get(name.lower(), name)
        found = shutil.which(executable)
        if found:
            return found
        # Let Windows resolve registered applications and App Paths.
        return executable if executable.lower().endswith(('.exe', '.bat', '.cmd', '.msc')) else ""
