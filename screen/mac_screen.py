import subprocess

from screen.screen_provider import ScreenProvider


class MacScreen(ScreenProvider):

    def capture(self, output_path: str) -> str:
        subprocess.run(
            ["screencapture", "-x", output_path],
            check=True
        )

        return output_path