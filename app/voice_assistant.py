
import re
import traceback

from audio.microphone.real_microphone import RealMicrophone
from audio.stt.whisper_stt import WhisperSTT
from audio.tts.windows_tts import WindowsTTS
from brain.llm.llm_factory import create_llm

from brain.brain_coordinator import BrainCoordinator
from brain.conversation.context import ConversationContext


class VoiceAssistant:

    def __init__(self):
        print("Initializing Ela...")

        self.microphone = RealMicrophone()
        self.stt = WhisperSTT()
        self.tts = WindowsTTS()

        self.context = ConversationContext()
        llm = create_llm()

        self.brain = BrainCoordinator(
            context=self.context,
            llm=llm
        )

        print("Ela is ready.")

    def run_once(self):
        audio = self.microphone.record()

        if not audio:
            print("No audio recorded; skipping.")
            return

        text = self.stt.transcribe(audio).strip()

        if not text:
            print("No reliable speech detected; skipping.")
            return

        # Ignore punctuation-only results.
        if not any(char.isalnum() for char in text):
            print("Invalid transcription; skipping.")
            return

        # Detect repeated hallucinated sentences.
        sentences = [
            part.strip().lower()
            for part in re.split(r"[.!?]+", text)
            if part.strip()
        ]

        if sentences:
            counts = {
                sentence: sentences.count(sentence)
                for sentence in set(sentences)
            }

            if max(counts.values()) >= 3:
                print("Repeated transcription detected; skipping.")
                return

        print(f"You: {text}")

        response = self.brain.process(text)

        print(f"Ela: {response}")

        if response:
            self.tts.speak(response)

    def run_forever(self):
        print("Ela is now listening continuously.")
        consecutive_errors = 0

        while True:
            try:
                self.run_once()
                consecutive_errors = 0

            except KeyboardInterrupt:
                print("\nEla stopped.")
                break

            except Exception as error:
                consecutive_errors += 1

                print(
                    f"Error ({consecutive_errors}/3): "
                    f"{type(error).__name__}: {error}"
                )

                traceback.print_exc()

                if consecutive_errors >= 3:
                    print("Too many consecutive errors. Ela stopped.")
                    break

            except Exception as error:
                consecutive_errors += 1
                print(f"Error ({consecutive_errors}/3): {error}")

                if consecutive_errors >= 3:
                    print("Too many consecutive errors. Ela stopped.")
                    break


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run_forever()
