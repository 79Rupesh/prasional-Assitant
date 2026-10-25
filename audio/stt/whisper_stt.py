
"""Whisper STT for English, Hindi and Hinglish."""

from dataclasses import dataclass
import os
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
    average_logprob: float = -10.0


class WhisperSTT(STTProvider):
    FRAME_SAMPLES = 320
    MIN_SPEECH_FRAME_RMS = 0.0015
    MIN_ACTIVE_FRAMES = 5
    # Short Hinglish commands often have lower confidence than long English
    # sentences. These values still reject clear no-speech/hallucination
    # output without throwing away normal commands such as "Ela, open Chrome".
    MIN_AVG_LOGPROB = -1.35
    MAX_NO_SPEECH_PROB = 0.80

    def __init__(self, model_name: str = None, model=None):
        model_name = (model_name or os.getenv("ELA_WHISPER_MODEL", "small")).strip()
        if not model_name:
            model_name = "small"
        self.language_preference = os.getenv(
            "ELA_WHISPER_LANGUAGE", "auto"
        ).strip().lower()
        if self.language_preference not in {"auto", "en", "hi"}:
            raise ValueError(
                "ELA_WHISPER_LANGUAGE must be 'auto', 'en', or 'hi'."
            )
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
            "beam_size": 3,
            "condition_on_previous_text": False,
            "no_speech_threshold": self.MAX_NO_SPEECH_PROB,
            "logprob_threshold": self.MIN_AVG_LOGPROB,
            "compression_ratio_threshold": 2.4,
            "initial_prompt": (
                "The assistant is called Ela. Commands may be in English, "
                "Hindi, or Hinglish."
            ),
            "verbose": False,
        }

        if language:
            options["language"] = language

        return self.model.transcribe(audio, **options)

    def _candidate(self, result):
        text = self._clean_text(result.get("text", ""))
        language = (result.get("language") or "").lower()
        segments = result.get("segments") or []
        reason = self._unreliable_reason(text, segments)
        if reason is None and language not in {"en", "hi"}:
            reason = f"unsupported language ({language or 'unknown'})"
        average_logprob = (
            sum(float(segment.get("avg_logprob", -10)) for segment in segments)
            / len(segments)
            if segments
            else -10.0
        )
        return TranscriptionResult(
            text=text,
            language=language,
            reliable=reason is None,
            reason=reason or "ok",
            average_logprob=average_logprob,
        )

    @classmethod
    def _filter_speech(cls, audio: np.ndarray):
        """Trim silence and reject noise/transient-only buffers before Whisper."""
        frame_count = int(np.ceil(audio.size / cls.FRAME_SAMPLES))
        frame_levels = np.empty(frame_count, dtype=np.float32)
        for index in range(frame_count):
            start = index * cls.FRAME_SAMPLES
            frame = audio[start:start + cls.FRAME_SAMPLES]
            frame_levels[index] = np.sqrt(np.mean(frame ** 2))

        reference_level = (
            float(np.percentile(frame_levels, 75)) if frame_levels.size else 0.0
        )
        threshold = max(cls.MIN_SPEECH_FRAME_RMS, reference_level * 0.25)
        active_frames = np.flatnonzero(frame_levels >= threshold)
        if active_frames.size < cls.MIN_ACTIVE_FRAMES:
            return None

        padding = int(0.1 * 16000)
        start = max(0, int(active_frames[0]) * cls.FRAME_SAMPLES - padding)
        end = min(
            audio.size,
            (int(active_frames[-1]) + 1) * cls.FRAME_SAMPLES + padding,
        )
        filtered = audio[start:end].copy()

        for index, level in enumerate(frame_levels):
            if level < threshold:
                frame_start = index * cls.FRAME_SAMPLES - start
                frame_end = frame_start + cls.FRAME_SAMPLES
                if frame_end > 0 and frame_start < filtered.size:
                    filtered[
                        max(0, frame_start):min(filtered.size, frame_end)
                    ] = 0.0

        return filtered

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

        audio = self._filter_speech(audio)
        if audio is None:
            self.last_result = TranscriptionResult(reason="no speech-level audio")
            print("No sustained speech detected; skipping Whisper.")
            return ""

        rms = float(np.sqrt(np.mean(audio ** 2)))
        peak = float(np.max(np.abs(audio)))
        print(f"Speech audio level: RMS={rms:.5f}, peak={peak:.5f}")

        try:
            initial_language = (
                None if self.language_preference == "auto"
                else self.language_preference
            )
            primary = self._candidate(
                self._run_transcription(audio, language=initial_language)
            )
        except Exception as error:
            self.last_result = TranscriptionResult(
                reason=f"Whisper error: {type(error).__name__}: {error}"
            )
            print(self.last_result.reason)
            return ""

        print("Detected language:", primary.language or "unknown")
        print("First transcription:", repr(primary.text))

        candidates = [primary]
        if not primary.reliable and self.language_preference == "auto":
            if primary.language in {"en", "hi"}:
                retry_languages = [primary.language]
                retry_languages.append("hi" if primary.language == "en" else "en")
            else:
                retry_languages = ["en", "hi"]

            # An auto-detection error must not force Hindi as the only retry:
            # try both supported spoken languages and keep the strongest valid
            # result. The maximum is three passes including the initial one.
            for retry_language in retry_languages:
                try:
                    retry_result = self._run_transcription(
                        audio,
                        language=retry_language,
                    )
                    retry_candidate = self._candidate(retry_result)
                    candidates.append(retry_candidate)
                    print(
                        f"{retry_language.upper()} retry:",
                        repr(retry_candidate.text),
                        f"reliable={retry_candidate.reliable}",
                        f"reason={retry_candidate.reason}",
                    )
                except Exception as error:
                    print(
                        f"{retry_language.upper()} retry failed: "
                        f"{type(error).__name__}: {error}"
                    )

        reliable_candidates = [
            candidate for candidate in candidates if candidate.reliable
        ]
        best = max(
            reliable_candidates,
            key=lambda candidate: candidate.average_logprob,
            default=primary,
        )

        self.last_result = best
        print(f"Whisper quality: reliable={best.reliable}, reason={best.reason}")
        if not best.reliable:
            print("No reliable transcription; skipping.")
            return ""

        print("Whisper recognized:", best.text)
        return best.text
