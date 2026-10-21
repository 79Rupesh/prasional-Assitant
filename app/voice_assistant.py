
import re
import time
import traceback

from audio.microphone.real_microphone import RealMicrophone
from audio.stt.whisper_stt import WhisperSTT
from audio.tts.windows_tts import WindowsTTS
from brain.llm.llm_factory import create_llm
from brain.brain_coordinator import BrainCoordinator
from brain.conversation.context import ConversationContext


class VoiceAssistant:
    WAKE_TIMEOUT_SECONDS = 12

    def __init__(self):
        print("Initializing Ela...")

        self.microphone = RealMicrophone()
        self.stt = WhisperSTT()
        self.tts = WindowsTTS()
        self.context = ConversationContext()

        llm = create_llm()
        self.brain = BrainCoordinator(
            context=self.context,
            llm=llm,
        )

        self.active_until = 0.0

        # Accept common English spellings produced by speech recognition.
        
        self.wake_pattern = re.compile(
            r"^\s*(?:(?:hey|hi)\s+)?"
            r"(?:ela|ella|aila|ayla|eila|एला)\b"
            r"[\s,.:;!?\-]*(.*)$",
            re.IGNORECASE,
        )


        print("Ela is ready.")

    def _extract_wake_command(self, text):
        match = self.wake_pattern.match(text.strip())
        if not match:
            return None

        return match.group(1).strip()

    def run_once(self):
        audio = self.microphone.record()

        if not audio:
            return

        text = self.stt.transcribe(audio).strip()

        if not text:
            print("No reliable speech detected; staying idle.")
            return

        print(f"Heard: {text}")

        # Ignore all speech unless Ela has been called or is already active.
        command = self._extract_wake_command(text)

        if command is not None:
            self.active_until = time.monotonic() + self.WAKE_TIMEOUT_SECONDS

            if not command:
                print("Wake word detected. Ela is active.")
                self.tts.speak("Haan, bolo.")
                return

            text = command
            print(f"Wake word detected. Command: {text}")

        elif time.monotonic() > self.active_until:
            print("Wake word not detected; ignoring speech.")
            return

        else:
            print("Ela is in active follow-up mode.")

        # Extend the interaction window for a follow-up command.
        self.active_until = time.monotonic() + self.WAKE_TIMEOUT_SECONDS

        response = self.brain.process(text)
        print(f"Ela: {response}")

        if response:
            self.tts.speak(response)

    def run_forever(self):
        print("Ela is listening in standby mode.")
        print("Say 'Ela' before your command.")

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


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run_forever()
