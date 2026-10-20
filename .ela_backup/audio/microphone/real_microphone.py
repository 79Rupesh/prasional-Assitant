
import sounddevice as sd
import numpy as np
from scipy.signal import resample_poly
from scipy.io.wavfile import write

from audio.microphone.base import Microphone


class RealMicrophone(Microphone):

    def record(self) -> bytes:
        print("Listening......")

        try:
            audio = sd.rec(
                int(5 * 48000),
                samplerate=48000,
                channels=2,
                dtype="int16",
                device=1
            )
            sd.wait()

            # Select the louder channel.
            levels = np.sqrt(
                np.mean(audio.astype(np.float32) ** 2, axis=0)
            )
            best_channel = int(np.argmax(levels))
            mono_audio = audio[:, best_channel]

            print("Channel RMS levels:", levels)
            print("Selected channel:", best_channel)

            # Convert 48000 Hz to 16000 Hz.
            audio_16k = resample_poly(
                mono_audio.astype(np.float32),
                up=1,
                down=3
            )

            # Save a test recording.
            audio_16k_int16 = np.clip(
                audio_16k, -32768, 32767
            ).astype(np.int16)

            write("mic_test.wav", 16000, audio_16k_int16)
            print("Saved recording to mic_test.wav")
            print("Recording finished.")

            return audio_16k_int16.tobytes()

        except Exception as error:
            print(f"Microphone recording error: {error}")
            return b""
