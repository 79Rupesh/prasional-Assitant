"""Windows microphone recorder that captures a complete spoken utterance.

It waits for speech to begin, records through short pauses, and stops after
silence. Audio is returned as 16 kHz mono int16 bytes for Whisper.
"""

from collections import deque
import math
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

    START_RMS_THRESHOLD = 220.0
    CONTINUE_RMS_THRESHOLD = 120.0
    START_TIMEOUT_SECONDS = 12.0
    END_SILENCE_SECONDS = 1.2
    MAX_UTTERANCE_SECONDS = 20.0
    PRE_ROLL_SECONDS = 0.30

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
                    chunk = np.asarray(chunk, dtype=np.int16).reshape(-1)

                    # RMS is calculated in int16 sample units, before normalization.
                    level = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

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

            audio_16k_int16 = np.concatenate(recorded_blocks).astype(np.int16, copy=False)

            # Diagnostic recording: this is overwritten on each recording.
            with wave.open("mic_test.wav", "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(self.TARGET_RATE)
                output.writeframes(audio_16k_int16.tobytes())

            duration = len(audio_16k_int16) / self.TARGET_RATE
            print(f"Recording finished. Duration: {duration:.2f} seconds")
            print("Saved recording to mic_test.wav")

            return audio_16k_int16.tobytes()

        except Exception as error:
            print(f"Microphone recording error: {type(error).__name__}: {error}")
            return b""
