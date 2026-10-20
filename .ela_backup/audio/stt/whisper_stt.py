
import re

import numpy as np
import whisper

from core.interfaces.stt import STTProvider


class WhisperSTT(STTProvider):

    def __init__(self, model_name: str = "small"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

    @staticmethod
    def _looks_unreliable(text: str) -> bool:
        text = text.strip()

        if not text:
            return True

        # Reject long, repeated-character hallucinations.
        if re.search(r"(.)\1{7,}", text):
            return True

        words = text.split()

        # Reject unusually long output from a short microphone clip.
        if len(words) > 45:
            return True

        return False

    def transcribe(self, audio_data: bytes) -> str:
        if not audio_data:
            print("No audio data received.")
            return ""

        audio = np.frombuffer(audio_data, dtype=np.int16)

        if audio.size == 0:
            print("Empty audio buffer.")
            return ""

        audio = audio.astype(np.float32) / 32768.0

        rms = float(np.sqrt(np.mean(audio ** 2)))
        peak = float(np.max(np.abs(audio)))

        print(f"Audio level: RMS={rms:.5f}, peak={peak:.5f}")

        if rms < 0.003:
            print("Audio is too quiet. Skipping.")
            return ""

        # First attempt: let Whisper detect the language itself.
        result = self.model.transcribe(
            audio,
            task="transcribe",
            fp16=False,
            temperature=0.0,
            beam_size=5,
            condition_on_previous_text=False,
            no_speech_threshold=0.5,
            verbose=False,
        )

        language = result.get("language", "")
        text = result.get("text", "").strip()

        print("Detected language:", language)
        print("First transcription:", repr(text))

        # If another language was detected but the output looks unreliable,
        # retry with the English-only model only when it is already loaded
        # as the current model. Never force English on multilingual speech.
        if self._looks_unreliable(text):
            print("Unreliable transcription detected; skipping.")
            return ""

        print("Whisper recognized:", text)
        return text
