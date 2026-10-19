import subprocess
from core.interfaces.tts import TTSProvider

class WindowsTTS(TTSProvider):
    """Text-to-speech using the Windows System.Speech API."""
    def speak(self, text: str) -> None:
        text = str(text or "").strip()
        if not text:
            return
        # Pass text through stdin to avoid PowerShell command injection/quoting issues.
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Speak([Console]::In.ReadToEnd())"
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            input=text, text=True, check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
