import subprocess

from core.interfaces.app_discovery import AppDiscoveryProvider


class MacAppDiscovery(AppDiscoveryProvider):

    def find(self, app_name: str) -> str:

        target = app_name.strip()

        if not target:
            return ""

        try:
            result = subprocess.run(
                [
                    "mdfind",
                    "kMDItemContentType == 'com.apple.application-bundle'"
                ],
                capture_output=True,
                text=True,
                check=True
            )

        except subprocess.CalledProcessError:
            return ""

        target_lower = target.lower()

        for path in result.stdout.splitlines():

            if not path.endswith(".app"):
                continue

            app_name_found = path.rsplit("/", 1)[-1][:-4]

            if app_name_found.lower() == target_lower:
                return path

        return ""