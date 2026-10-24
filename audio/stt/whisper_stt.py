
"""Whisper STT for English, Hindi and Hinglish."""

from dataclasses import dataclass
import re

import numpy as np
import whisper

from core.interfaces.stt import STTProvider


@dataclass(frozen=True)
class TranscriptionResult:
    """A quality-gated speech hypothesis for callers that trigger actions."""
    text: str = ""
    language: str = ""
    reliable: bool = False
    reason: str = "no transcription"


class WhisperSTT(STTProvider):
    MIN_RMS = 0.002
    MIN_AVG_LOGPROB = -1.0
    MAX_NO_SPEECH_PROB = 0.65

    def __init__(self, model_name: str = "small", model=None):
        print("Loading Whisper model...")
        self.model = model if model is not None else whisper.load_model(model_name)
        self.last_result = TranscriptionResult()
        print("Whisper model loaded.")

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "")).strip()

    @classmethod
    def _unreliable_reason(cls, text: str, segments=None):
        text = cls._clean_text(text)

        if not text:
            return "empty transcript"

        if re.search(r"(.)\1{7,}", text):
            return "repeated characters"

        words = text.split()

        normalized = [
            re.sub(r"[^\w\u0900-\u097f]", "", word.lower())
            for word in words
        ]
        normalized = [word for word in normalized if word]

        if len(normalized) >= 5 and len(set(normalized)) <= 2:
            return "repeated words"

        suspicious = (
            "the speaker may mix",
            "preserve the words actually spoken",
            "thanks for watching",
            "thank you for watching",
            "subscribe to my channel",
        )

        if any(phrase in text.lower() for phrase in suspicious):
            return "known Whisper hallucination"

        if not segments:
            return "no speech segments"

        average_logprob = sum(
            float(segment.get("avg_logprob", -10)) for segment in segments
        ) / len(segments)
        if average_logprob < cls.MIN_AVG_LOGPROB:
            return f"low confidence ({average_logprob:.2f})"

        if all(
            float(segment.get("no_speech_prob", 0)) > cls.MAX_NO_SPEECH_PROB
            for segment in segments
        ):
            return "Whisper detected no speech"

        return None

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
            "no_speech_threshold": self.MAX_NO_SPEECH_PROB,
            "logprob_threshold": self.MIN_AVG_LOGPROB,
            "compression_ratio_threshold": 2.4,
            "verbose": False,
        }

        if language:
            options["language"] = language

        return self.model.transcribe(audio, **options)

    def _candidate(self, result):
        text = self._clean_text(result.get("text", ""))
        language = (result.get("language") or "").lower()
        reason = self._unreliable_reason(text, result.get("segments") or [])
        if reason is None and language not in {"en", "hi"}:
            reason = f"unsupported language ({language or 'unknown'})"
        return TranscriptionResult(
            text=text,
            language=language,
            reliable=reason is None,
            reason=reason or "ok",
        )

    def transcribe(self, audio_data: bytes) -> str:
        self.last_result = TranscriptionResult()
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

        if rms < self.MIN_RMS:
            self.last_result = TranscriptionResult(reason="audio too quiet")
            print("Audio is too quiet. Skipping.")
            return ""

        try:
            primary = self._candidate(self._run_transcription(audio))
        except Exception as error:
            self.last_result = TranscriptionResult(
                reason=f"Whisper error: {type(error).__name__}"
            )
            print(self.last_result.reason)
            return ""

        best = primary
        print("Detected language:", primary.language or "unknown")
        print("First transcription:", repr(primary.text))

        # A forced Hindi decode is expensive.  It is useful for an unknown or
        # Hindi decode that failed quality checks, but retrying every mistaken
        # Bengali/other-language guess makes the assistant unresponsive.
        # Unexpected-language, low-quality text is rejected safely instead.
        if not primary.reliable and primary.language in {"", "hi"}:
            try:
                hindi_result = self._run_transcription(
                    audio,
                    language="hi",
                )

                hindi_candidate = self._candidate(hindi_result)
                print("Hindi retry:", repr(hindi_candidate.text))

                if hindi_candidate.reliable and not primary.reliable:
                    best = hindi_candidate

            except Exception as error:
                print(
                    f"Hindi retry failed: "
                    f"{type(error).__name__}: {error}"
                )

        self.last_result = best
        print(f"Whisper quality: reliable={best.reliable}, reason={best.reason}")
        if not best.reliable:
            print("No reliable transcription; skipping.")
            return ""

        print("Whisper recognized:", ascii(best.text))
        return best.text
