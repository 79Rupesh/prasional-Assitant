"""Fast tests for speech quality gating and text wake-word state transitions."""

import unittest
from unittest.mock import MagicMock

import numpy as np

from app.voice_assistant import VoiceAssistant, WAKE_WORD_PATTERN
from audio.stt.whisper_stt import WhisperSTT


class FakeWhisper:
    def __init__(self, results):
        self.results = iter(results)

    def transcribe(self, audio, **kwargs):
        return next(self.results)


def whisper_result(text, language="en", logprob=-0.2, no_speech=0.05):
    return {
        "text": text,
        "language": language,
        "segments": [{"avg_logprob": logprob, "no_speech_prob": no_speech}],
    }


class WhisperSafetyTests(unittest.TestCase):
    def test_rejects_repeated_hallucination(self):
        stt = WhisperSTT(model=FakeWhisper([
            whisper_result("Thank you. " * 6),
        ]))
        audio = (np.ones(1600, dtype=np.int16) * 1000).tobytes()
        self.assertEqual(stt.transcribe(audio), "")
        self.assertFalse(stt.last_result.reliable)

    def test_rejects_bad_unexpected_language_after_supported_language_retries(self):
        model = FakeWhisper([
            whisper_result("word " * 8, "bn"),
            whisper_result("word " * 8, "bn"),
            whisper_result("word " * 8, "bn"),
        ])
        stt = WhisperSTT(model=model)
        audio = (np.ones(1600, dtype=np.int16) * 1000).tobytes()
        self.assertEqual(stt.transcribe(audio), "")
        self.assertFalse(stt.last_result.reliable)

    def test_rejects_confident_transcript_in_unsupported_language(self):
        model = FakeWhisper([whisper_result("open youtube", "bn")])
        stt = WhisperSTT(model=model)
        audio = (np.ones(1600, dtype=np.int16) * 1000).tobytes()
        self.assertEqual(stt.transcribe(audio), "")
        self.assertIn("unsupported language", stt.last_result.reason)

    def test_accepts_clear_command(self):
        stt = WhisperSTT(model=FakeWhisper([whisper_result("Ela, open YouTube")]))
        audio = (np.ones(1600, dtype=np.int16) * 1000).tobytes()
        self.assertEqual(stt.transcribe(audio), "Ela, open YouTube")
        self.assertTrue(stt.last_result.reliable)

    def test_accepts_a_short_lower_confidence_command(self):
        stt = WhisperSTT(model=FakeWhisper([
            whisper_result("Ela open Chrome", logprob=-1.2),
        ]))
        audio = (np.ones(1600, dtype=np.int16) * 1000).tobytes()
        self.assertEqual(stt.transcribe(audio), "Ela open Chrome")
        self.assertTrue(stt.last_result.reliable)

    def test_accepts_a_quiet_recording_after_silence_is_included(self):
        stt = WhisperSTT(model=FakeWhisper([
            whisper_result("Ela open Chrome"),
        ]))
        samples = np.arange(16000, dtype=np.float32)
        quiet_speech = (
            np.sin(samples * 2 * np.pi * 220 / 16000) * 120
        ).astype(np.int16)
        audio = np.concatenate((
            np.zeros(3200, dtype=np.int16),
            quiet_speech,
        )).tobytes()
        self.assertEqual(stt.transcribe(audio), "Ela open Chrome")
        self.assertTrue(stt.last_result.reliable)


class VoiceWakeTests(unittest.TestCase):
    def make_assistant(self, text, reliable=True):
        assistant = VoiceAssistant.__new__(VoiceAssistant)
        assistant.microphone = MagicMock(record=MagicMock(return_value=b"audio"))
        assistant.stt = MagicMock()
        assistant.stt.transcribe.return_value = text
        assistant.stt.last_result = MagicMock(reliable=reliable)
        assistant.tts = MagicMock()
        assistant.brain = MagicMock()
        assistant.active_until = 0.0
        assistant.wake_timeout_seconds = 45
        import re
        assistant.wake_pattern = re.compile(r"^\s*(?:ela|ella)[\s,.:;!?-]*(.*)$", re.I)
        assistant.hindi_wake_pattern = re.compile(r"^\s*(?:\u090f\u0932\u093e)[\s,.:;!?-]*(.*)$")
        return assistant

    def test_background_speech_does_not_reach_brain(self):
        assistant = self.make_assistant("open youtube")
        assistant.run_once()
        assistant.brain.process.assert_not_called()

    def test_reliable_wake_command_reaches_brain(self):
        assistant = self.make_assistant("Ela, open YouTube")
        assistant.brain.process.return_value = "Opened YouTube"
        assistant.run_once()
        assistant.brain.process.assert_called_once_with("open YouTube")

    def test_unreliable_wake_text_is_ignored(self):
        assistant = self.make_assistant("Ela, open YouTube", reliable=False)
        assistant.run_once()
        assistant.brain.process.assert_not_called()

    def test_real_hindi_wake_word_is_recognized(self):
        assistant = VoiceAssistant.__new__(VoiceAssistant)
        import re
        assistant.wake_pattern = re.compile(WAKE_WORD_PATTERN, re.IGNORECASE)
        self.assertEqual(
            assistant._extract_wake_command("\u090f\u0932\u093e, \u0915\u094d\u0930\u094b\u092e \u0916\u094b\u0932\u094b"),
            "\u0915\u094d\u0930\u094b\u092e \u0916\u094b\u0932\u094b",
        )

    def test_wake_word_cancel_returns_to_standby(self):
        assistant = self.make_assistant("Ela, बंद करो")
        assistant.run_once()
        assistant.brain.process.assert_not_called()
        assistant.brain.task_dispatcher.task_state.cancel_active.assert_called_once()


if __name__ == "__main__":
    unittest.main()
