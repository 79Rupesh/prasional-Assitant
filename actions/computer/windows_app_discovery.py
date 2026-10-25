import os
import shutil
import subprocess
import json
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
            "whatsapp": "WhatsApp",
        }
        executable = aliases.get(name.lower(), name)
        found = shutil.which(executable)
        if found:
            return found

        # Microsoft Store apps such as WhatsApp do not expose a normal .exe
        # through PATH. Resolve their Start menu AppID without launching them.
        try:
            result = subprocess.run(
                [
                    "powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                    "Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            apps = json.loads(result.stdout or "[]")
            if isinstance(apps, dict):
                apps = [apps]
            requested = name.casefold()
            for app in apps:
                app_name = str(app.get("Name", "")).strip()
                app_id = str(app.get("AppID", "")).strip()
                if app_name.casefold() == requested and app_id:
                    return "shell:AppsFolder\\" + app_id
        except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError):
            pass

        # Let Windows resolve registered applications and App Paths.
        return executable if executable.lower().endswith(('.exe', '.bat', '.cmd', '.msc')) else ""
