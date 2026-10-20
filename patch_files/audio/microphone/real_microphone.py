"""Windows microphone recorder that captures a complete spoken utterance.

It waits for speech to begin, records through short pauses, and stops after
silence. Audio is returned as 16 kHz mono int16 bytes for Whisper.
"""

from collections import deque
import math

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from scipy.signal import resample_poly

from audio.microphone.base import Microphone


class RealMicrophone(Microphone):
    SAMPLE_RATE = 48000
    TARGET_RATE = 16000
    CHANNELS = 2
    DEVICE = 1  # This is the working microphone device shown in your logs.
    BLOCK_SIZE = 1024

    START_RMS_THRESHOLD = 220.0
    CONTINUE_RMS_THRESHOLD = 120.0
    START_TIMEOUT_SECONDS = 12.0
    END_SILENCE_SECONDS = 1.4
    MAX_UTTERANCE_SECONDS = 25.0
    PRE_ROLL_SECONDS = 0.25

    def record(self) -> bytes:
        print("Listening... Speak normally; recording stops after you finish speaking.")

        blocks_per_second = self.SAMPLE_RATE / self.BLOCK_SIZE
        pre_roll_blocks = max(1, math.ceil(self.PRE_ROLL_SECONDS * blocks_per_second))
        silence_limit = max(1, math.ceil(self.END_SILENCE_SECONDS * blocks_per_second))
        start_timeout_blocks = max(1, math.ceil(self.START_TIMEOUT_SECONDS * blocks_per_second))
        max_utterance_blocks = max(1, math.ceil(self.MAX_UTTERANCE_SECONDS * blocks_per_second))

        pre_roll = deque(maxlen=pre_roll_blocks)
        recorded_blocks = []
        speech_started = False
        captured_after_start = 0
        silent_blocks = 0

        try:
            with sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype="int16",
                device=self.DEVICE,
                blocksize=self.BLOCK_SIZE,
            ) as stream:
                for block_index in range(start_timeout_blocks + max_utterance_blocks):
                    chunk, overflowed = stream.read(self.BLOCK_SIZE)
                    chunk = np.asarray(chunk, dtype=np.int16)

                    # RMS is calculated in int16 sample units, before normalization.
                    channel_levels = np.sqrt(
                        np.mean(chunk.astype(np.float32) ** 2, axis=0)
                    )
                    level = float(np.max(channel_levels))

                    if not speech_started:
                        pre_roll.append(chunk.copy())

                        if level >= self.START_RMS_THRESHOLD:
                            speech_started = True
                            recorded_blocks.extend(list(pre_roll))
                            captured_after_start = len(recorded_blocks)
                            print("Speech detected. Recording your full sentence...")
                        elif block_index + 1 >= start_timeout_blocks:
                            print("No speech detected; skipping this listening cycle.")
                            return b""
                        continue

                    recorded_blocks.append(chunk.copy())
                    captured_after_start += 1

                    if level < self.CONTINUE_RMS_THRESHOLD:
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

            stereo_audio = np.concatenate(recorded_blocks, axis=0)

            # Choose the clearer/louder microphone channel and convert 48 kHz to 16 kHz.
            channel_levels = np.sqrt(
                np.mean(stereo_audio.astype(np.float32) ** 2, axis=0)
            )
            best_channel = int(np.argmax(channel_levels))
            mono_audio = stereo_audio[:, best_channel].astype(np.float32)

            audio_16k = resample_poly(mono_audio, up=1, down=3)
            audio_16k_int16 = np.clip(audio_16k, -32768, 32767).astype(np.int16)

            # Diagnostic recording: this is overwritten on each recording.
            write("mic_test.wav", self.TARGET_RATE, audio_16k_int16)

            duration = len(audio_16k_int16) / self.TARGET_RATE
            print(f"Recording finished. Duration: {duration:.2f} seconds")
            print("Saved recording to mic_test.wav")

            return audio_16k_int16.tobytes()

        except Exception as error:
            print(f"Microphone recording error: {type(error).__name__}: {error}")
            return b""
