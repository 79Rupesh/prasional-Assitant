
import numpy as np
import whisper

from core.interfaces.stt import STTProvider


class WhisperSTT(STTProvider):

    def __init__(self, model_name: str = "small"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

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

        result = self.model.transcribe(
            audio,
            task="transcribe",
            fp16=False,
            temperature=0.0,
            beam_size=5,
            condition_on_previous_text=False,
            no_speech_threshold=0.5,
            logprob_threshold=-1.0,
            compression_ratio_threshold=2.4,
            verbose=False,
        )

        language = result.get("language")
        text = result.get("text", "").strip()

        print("Detected language:", language)
        print("Raw Whisper result:", repr(text))

        if not text:
            print("No reliable speech transcription returned.")
            return ""

        if not any(char.isalnum() for char in text):
            print("Invalid transcription; skipping.")
            return ""

        print("Whisper recognized:", text)
        return text
