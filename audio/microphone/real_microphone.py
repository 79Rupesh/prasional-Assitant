"""Windows microphone recorder that captures a complete spoken utterance.

It waits for speech to begin, records through short pauses, and stops after
silence. Audio is returned as 16 kHz mono int16 bytes for Whisper.
"""

from collections import deque
import math
import os
import tempfile
import wave

import numpy as np
import sounddevice as sd

from audio.microphone.base import Microphone


class RealMicrophone(Microphone):
    # Whisper expects 16 kHz mono.  ``None`` lets sounddevice select the
    # current default input instead of relying on a stale device index.
    SAMPLE_RATE = 16000
    TARGET_RATE = 16000
    CHANNELS = 1
    DEVICE = None
    BLOCK_SIZE = 1024

    # These are deliberately low baselines. Actual thresholds are calibrated
    # from ambient noise at the start of each listening cycle.
    MIN_START_RMS_THRESHOLD = 75.0
    MIN_CONTINUE_RMS_THRESHOLD = 35.0
    MAX_START_RMS_THRESHOLD = 900.0
    START_TIMEOUT_SECONDS = 12.0
    END_SILENCE_SECONDS = 1.6
    MAX_UTTERANCE_SECONDS = 45.0
    PRE_ROLL_SECONDS = 0.30
    CALIBRATION_SECONDS = 0.45
    START_CONFIRM_WINDOW_BLOCKS = 3
    START_CONFIRM_BLOCKS = 2
    MIN_ACTIVE_BLOCKS = 3

    def __init__(self, device=None):
        self.device = self._resolve_device(device)

    @staticmethod
    def _resolve_device(device):
        """Use an explicit device only when the user has configured one."""
        if device is not None:
            return device

        configured = os.getenv("ELA_MIC_DEVICE", "").strip()
        if not configured:
            return None

        try:
            return int(configured)
        except ValueError:
            return configured

    @staticmethod
    def _sensitivity() -> float:
        """Return a safe user-tunable sensitivity multiplier (default: 1)."""
        try:
            value = float(os.getenv("ELA_MIC_SENSITIVITY", "1.0"))
        except ValueError:
            print("Invalid ELA_MIC_SENSITIVITY; using 1.0.")
            return 1.0
        return min(3.0, max(0.5, value))

    @classmethod
    def _thresholds_for_noise(cls, ambient_rms: float, sensitivity: float):
        """Calculate speech thresholds without making quiet microphones unusable."""
        start = max(cls.MIN_START_RMS_THRESHOLD, ambient_rms * 2.5)
        start = min(cls.MAX_START_RMS_THRESHOLD, start) / sensitivity
        continuation = max(cls.MIN_CONTINUE_RMS_THRESHOLD, ambient_rms * 1.3)
        # Continuation must stay below the start threshold; otherwise speech
        # could be detected and immediately treated as silence in a loud room.
        continuation = min(continuation / sensitivity, start * 0.65)
        return start, continuation

    @staticmethod
    def _rms(chunk: np.ndarray) -> float:
        return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

    @classmethod
    def _speech_started(cls, levels, threshold: float) -> bool:
        return sum(level >= threshold for level in levels) >= cls.START_CONFIRM_BLOCKS

    def _calibrate(self, stream, blocks: int) -> float:
        levels = []
        for _ in range(max(1, blocks)):
            chunk, overflowed = stream.read(self.BLOCK_SIZE)
            if overflowed:
                print("Microphone overflow during calibration; continuing.")
            levels.append(self._rms(np.asarray(chunk, dtype=np.int16).reshape(-1)))
        return float(np.median(levels)) if levels else 0.0

    def record(self) -> bytes:
        print("Calibrating microphone; please stay quiet for a moment...")

        blocks_per_second = self.SAMPLE_RATE / self.BLOCK_SIZE
        pre_roll_blocks = max(1, math.ceil(self.PRE_ROLL_SECONDS * blocks_per_second))
        silence_limit = max(1, math.ceil(self.END_SILENCE_SECONDS * blocks_per_second))
        start_timeout_blocks = max(1, math.ceil(self.START_TIMEOUT_SECONDS * blocks_per_second))
        max_utterance_blocks = max(1, math.ceil(self.MAX_UTTERANCE_SECONDS * blocks_per_second))
        calibration_blocks = max(1, math.ceil(self.CALIBRATION_SECONDS * blocks_per_second))

        pre_roll = deque(maxlen=pre_roll_blocks)
        recent_levels = deque(maxlen=self.START_CONFIRM_WINDOW_BLOCKS)
        recorded_blocks = []
        speech_started = False
        captured_after_start = 0
        active_blocks = 0
        silent_blocks = 0

        try:
            with sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype="int16",
                device=self.device,
                blocksize=self.BLOCK_SIZE,
            ) as stream:
                ambient_rms = self._calibrate(stream, calibration_blocks)
                start_threshold, continue_threshold = self._thresholds_for_noise(
                    ambient_rms,
                    self._sensitivity(),
                )
                print(
                    "Listening... Speak normally. "
                    f"Mic noise={ambient_rms:.0f}, speech threshold={start_threshold:.0f}."
                )

                for block_index in range(start_timeout_blocks + max_utterance_blocks):
                    chunk, overflowed = stream.read(self.BLOCK_SIZE)
                    chunk = np.asarray(chunk, dtype=np.int16).reshape(-1)

                    # RMS is calculated in int16 sample units, before normalization.
                    level = self._rms(chunk)
                    if overflowed:
                        print("Microphone overflow detected; audio may be incomplete.")

                    if not speech_started:
                        pre_roll.append(chunk.copy())
                        recent_levels.append(level)

                        if self._speech_started(recent_levels, start_threshold):
                            speech_started = True
                            recorded_blocks.extend(list(pre_roll))
                            captured_after_start = len(recorded_blocks)
                            active_blocks = sum(
                                prior_level >= start_threshold
                                for prior_level in recent_levels
                            )
                            print("Speech detected. Recording your full sentence...")
                        elif block_index + 1 >= start_timeout_blocks:
                            print("No speech detected; skipping this listening cycle.")
                            return b""
                        continue

                    recorded_blocks.append(chunk.copy())
                    captured_after_start += 1
                    if level >= start_threshold:
                        active_blocks += 1

                    if level < continue_threshold:
                        silent_blocks += 1
                    else:
                        silent_blocks = 0

                    if silent_blocks >= silence_limit:
                        break

                    if captured_after_start >= max_utterance_blocks:
                        print("Maximum utterance duration reached.")
                        break

            if not recorded_blocks:
                print("No audio captured.")
                return b""

            if active_blocks < self.MIN_ACTIVE_BLOCKS:
                print(
                    "Speech was too brief or inconsistent; "
                    "skipping this listening cycle."
                )
                return b""

            audio_16k_int16 = np.concatenate(recorded_blocks).astype(np.int16, copy=False)

            duration = len(audio_16k_int16) / self.TARGET_RATE
            print(f"Recording finished. Duration: {duration:.2f} seconds")

            # Audio stays in memory unless the user explicitly enables a
            # diagnostic copy. Never overwrite a project file with mic audio.
            if os.getenv("ELA_SAVE_MIC_DIAGNOSTIC", "false").strip().lower() in {
                "1", "true", "yes", "on",
            }:
                diagnostic_path = os.path.join(
                    tempfile.gettempdir(), "ela_mic_diagnostic.wav"
                )
                with wave.open(diagnostic_path, "wb") as output:
                    output.setnchannels(1)
                    output.setsampwidth(2)
                    output.setframerate(self.TARGET_RATE)
                    output.writeframes(audio_16k_int16.tobytes())
                print(f"Saved opt-in microphone diagnostic to {diagnostic_path}")

            return audio_16k_int16.tobytes()

        except Exception as error:
            print(f"Microphone recording error: {type(error).__name__}: {error}")
            return b""
