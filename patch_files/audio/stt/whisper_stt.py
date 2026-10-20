"""Whisper STT with automatic English/Hindi detection and safer fallbacks."""

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

        # Catch hallucinations made from one character repeated many times.
        if re.search(r"(.)\1{7,}", text):
            return True

        words = text.split()
        if len(words) > 45:
            return True

        # Reject output consisting almost entirely of the same word.
        normalized_words = [re.sub(r"\W+", "", word.lower()) for word in words]
        normalized_words = [word for word in normalized_words if word]
        if len(normalized_words) >= 6 and len(set(normalized_words)) <= 2:
            return True

        return False

    def _run_transcription(self, audio: np.ndarray, language: str = None, prompt: str = None):
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

        # Do not force a language on the first pass. Whisper gets to detect it.
        if language:
            options["language"] = language
        if prompt:
            options["initial_prompt"] = prompt

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

        # Pass 1: multilingual automatic language detection.
        try:
            first_result = self._run_transcription(audio)
        except Exception as error:
            print(f"Whisper transcription error: {type(error).__name__}: {error}")
            return ""

        language = (first_result.get("language") or "").lower()
        text = (first_result.get("text") or "").strip()
        print("Detected language:", language or "unknown")
        print("First transcription:", repr(text))

        # English is refined with a light domain prompt. Hindi remains multilingual.
        english_prompt = (
            "Clear, natural English speech. Preserve the words actually spoken. "
            "The speaker may mention computers, websites, Chrome, Facebook, YouTube, "
            "artificial intelligence, or ask general questions."
        )

        if language == "en":
            try:
                refined_result = self._run_transcription(
                    audio,
                    language="en",
                    prompt=english_prompt,
                )
                refined_text = (refined_result.get("text") or "").strip()
                print("English refinement:", repr(refined_text))

                if not self._looks_unreliable(refined_text):
                    text = refined_text
            except Exception as error:
                print(f"English refinement skipped: {type(error).__name__}: {error}")

        elif language not in {"hi", ""} or self._looks_unreliable(text):
            # The project is intended for English/Hindi/Hinglish. When Whisper
            # guesses an unrelated language or produces obvious gibberish, retry English.
            try:
                fallback_result = self._run_transcription(
                    audio,
                    language="en",
                    prompt=english_prompt,
                )
                fallback_text = (fallback_result.get("text") or "").strip()
                print("English fallback:", repr(fallback_text))

                if not self._looks_unreliable(fallback_text):
                    text = fallback_text
                elif self._looks_unreliable(text):
                    print("No reliable transcription; skipping.")
                    return ""
            except Exception as error:
                print(f"English fallback failed: {type(error).__name__}: {error}")
                if self._looks_unreliable(text):
                    return ""

        if self._looks_unreliable(text):
            print("Unreliable transcription; skipping.")
            return ""

        print("Whisper recognized:", text)
        return text
