import numpy as np

from audio.stt.whisper_stt import WhisperSTT


class FakeWhisper:
    def __init__(self, results):
        self.results = iter(results)
        self.options = []

    def transcribe(self, audio, **kwargs):
        self.options.append(kwargs)
        return next(self.results)


def whisper_result(text, language="en", logprob=-0.2, no_speech=0.05):
    return {
        "text": text,
        "language": language,
        "segments": [{"avg_logprob": logprob, "no_speech_prob": no_speech}],
    }


def speech_audio():
    samples = np.arange(16000, dtype=np.float32)
    speech = (np.sin(samples * 2 * np.pi * 220 / 16000) * 4000).astype(np.int16)
    return np.concatenate((np.zeros(3200, dtype=np.int16), speech)).tobytes()


def test_noise_at_reported_rms_is_rejected_before_whisper():
    model = FakeWhisper([whisper_result("Thank you.")])
    stt = WhisperSTT(model=model)
    noise = np.full(16000, 17, dtype=np.int16)

    assert stt.transcribe(noise.tobytes()) == ""
    assert model.options == []
    assert stt.last_result.reason == "no speech-level audio"


def test_short_loud_transient_is_not_treated_as_speech():
    model = FakeWhisper([whisper_result("Thank you.")])
    stt = WhisperSTT(model=model)
    transient = np.zeros(16000, dtype=np.int16)
    transient[:320] = 2000

    assert stt.transcribe(transient.tobytes()) == ""
    assert model.options == []


def test_brief_click_does_not_mask_the_following_speech():
    model = FakeWhisper([whisper_result("open Chrome")])
    stt = WhisperSTT(model=model)
    audio = np.frombuffer(speech_audio(), dtype=np.int16).copy()
    audio[3200:3520] = 30000

    assert stt.transcribe(audio.tobytes()) == "open Chrome"
    assert stt.last_result.reliable


def test_unsupported_auto_language_retries_english_and_hindi():
    model = FakeWhisper([
        whisper_result("unrelated transcript", "yo", logprob=-0.1),
        whisper_result("open Chrome", "en", logprob=-0.2),
        whisper_result("अन्य शब्द", "hi", logprob=-0.8),
    ])
    stt = WhisperSTT(model=model)

    assert stt.transcribe(speech_audio()) == "open Chrome"
    assert [options.get("language") for options in model.options] == [
        None, "en", "hi"
    ]
    assert stt.last_result.reliable
    assert stt.last_result.language == "en"


def test_repeated_devanagari_hallucination_never_becomes_a_command():
    model = FakeWhisper([
        whisper_result("ॐ ॐ ॐ ॐ ॐ ॐ", "hi"),
        whisper_result("ॐ ॐ ॐ ॐ ॐ ॐ", "hi"),
        whisper_result("ॐ ॐ ॐ ॐ ॐ ॐ", "hi"),
    ])
    stt = WhisperSTT(model=model)

    assert stt.transcribe(speech_audio()) == ""
    assert not stt.last_result.reliable
    assert stt.last_result.reason == "repeated words"
