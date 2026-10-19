import os
import shutil
import subprocess
from core.interfaces.action import Action

class OpenAppAction(Action):
    def execute(self, value: str) -> str:
        app_name = value.strip()
        if not app_name:
            return "No application specified."
        target = shutil.which(app_name) or app_name
        try:
            if os.path.exists(target):
                os.startfile(target)
            else:
                subprocess.Popen([target], shell=False)
            return f"Opened {app_name}"
        except (OSError, subprocess.SubprocessError) as error:
            return f"Unable to open {app_name}: {error}"
