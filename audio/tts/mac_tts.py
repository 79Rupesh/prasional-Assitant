import subprocess

from core.interfaces.tts import TTSProvider


class MacTTS(TTSProvider):

    def speak(self, text: str) -> None:
        subprocess.run(
            ["say", "-v", "Tara", text],
            check=True
        )