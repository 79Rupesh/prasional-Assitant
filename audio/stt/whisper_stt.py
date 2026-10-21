
"""Whisper STT for English, Hindi and Hinglish."""

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
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "")).strip()

    @classmethod
    def _looks_unreliable(cls, text: str) -> bool:
        text = cls._clean_text(text)

        if not text:
            return True

        if re.search(r"(.)\1{7,}", text):
            return True

        words = text.split()

        if len(words) > 45:
            return True

        normalized = [
            re.sub(r"[^\w]", "", word.lower())
            for word in words
        ]
        normalized = [word for word in normalized if word]

        if len(normalized) >= 6 and len(set(normalized)) <= 2:
            return True

        suspicious = (
            "the speaker may mix",
            "preserve the words actually spoken",
            "thanks for watching",
            "subscribe to my channel",
        )

        if any(phrase in text.lower() for phrase in suspicious):
            return True

        return False

    def _run_transcription(
        self,
        audio: np.ndarray,
        language: str = None,
    ):
        options = {
            "task": "transcribe",
            "fp16": False,
            "temperature": 0.0,
            "beam_size": 5,
            "condition_on_previous_text": False,
            "no_speech_threshold": 0.6,
            "logprob_threshold": -1.0,
            "compression_ratio_threshold": 2.4,
            "verbose": False,
        }

        if language:
            options["language"] = language

        return self.model.transcribe(audio, **options)

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

        try:
            result = self._run_transcription(audio)
        except Exception as error:
            print(
                f"Whisper error: {type(error).__name__}: {error}"
            )
            return ""

        language = (result.get("language") or "").lower()
        text = self._clean_text(result.get("text", ""))

        print("Detected language:", language or "unknown")
        print("First transcription:", repr(text))

        # If automatic detection looks wrong, retry in Hindi without a prompt.
        if language not in {"en", "hi"} or self._looks_unreliable(text):
            try:
                hindi_result = self._run_transcription(
                    audio,
                    language="hi",
                )

                hindi_text = self._clean_text(
                    hindi_result.get("text", "")
                )
                print("Hindi retry:", repr(hindi_text))

                if not self._looks_unreliable(hindi_text):
                    text = hindi_text

            except Exception as error:
                print(
                    f"Hindi retry failed: "
                    f"{type(error).__name__}: {error}"
                )

        if self._looks_unreliable(text):
            print("No reliable transcription; skipping.")
            return ""

        print("Whisper recognized:", text)
        return text
