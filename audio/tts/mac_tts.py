import subprocess

from core.interfaces.tts import TTSProvider


class MacTTS(TTSProvider):

    def speak(self, text: str) -> None:
        text = str(text or "").strip()
        if not text:
            return
        subprocess.run(
            ["say", text],
            check=True
        )
