import re
import time

from audio.microphone.real_microphone import RealMicrophone
from audio.stt.whisper_stt import WhisperSTT
from brain.llm.llm_factory import create_llm
from brain.brain_coordinator import BrainCoordinator
from brain.conversation.context import ConversationContext
from core.config.settings import settings
from core.platform_support import create_tts
from remote.phone_call_server import PhoneCallServer


WAKE_WORD_PATTERN = (
    r"^\s*"
    r"(?:(?:hello|hey|hi)\s+)?"
    r"(?:ela|ella|aila|ayla|eila|\u090f\u0932\u093e|\u0907\u0932\u093e|\u0908\u0932\u093e)"
    r"(?=$|[\s,.:;!?-])"
    r"[\s,.:;!?-]*"
    r"(.*)$"
)

OPEN_COMMAND_WITH_AI_SUFFIX = re.compile(
    r"^\s*((?:open|launch|start|go\s+to|visit|navigate\s+to)\s+.+?)"
    r"\s+ai[,.!?]*$",
    re.IGNORECASE,
)

CANCEL_PHRASES = {
    "stop", "cancel", "ruko", "band karo",
    "\u0930\u0941\u0915\u094b", "\u0930\u0941\u0915 \u091c\u093e\u0913",
    "\u092c\u0902\u0926 \u0915\u0930\u094b", "\u092c\u0938",
}


class VoiceAssistant:
    """
    Ela voice assistant.

    Features:
    - Wake-word detection in English and Hindi.
    - Short active conversation window after wake word.
    - Local/LLM response through BrainCoordinator.
    - Voice responses through the native Windows or macOS speech service.
    - Session-only conversation context.
    """

    def __init__(self):
        print("Initializing Ela...")

        self.microphone = RealMicrophone()
        self.stt = WhisperSTT()
        self.tts = create_tts()
        self.context = ConversationContext()

        # Initialize the LLM if configured.
        try:
            llm = create_llm()
        except (ImportError, ValueError) as error:
            print(
                f"LLM unavailable ({type(error).__name__}); "
                "local assistant features remain enabled."
            )
            llm = None

        self.brain = BrainCoordinator(
            context=self.context,
            llm=llm,
        )
        self.phone_server = None
        if PhoneCallServer.enabled():
            # Keep remote confirmation state separate from the local mic while
            # serializing actual desktop actions through the shared dispatcher lock.
            phone_brain = BrainCoordinator(
                context=ConversationContext(),
                llm=None,
            )
            self.phone_server = PhoneCallServer(phone_brain)
            self.phone_server.start()

        # Conversation remains active for a limited time after wake word.
        self.active_until = 0.0
        self.wake_timeout_seconds = settings.wake_timeout_seconds

        # Accept common English and Hindi wake-word transcriptions.
        #
        # Supported examples:
        #   Ela, open Chrome
        #   Ella, how are you?
        #   Hello Ela, how are you?
        #   Hey Ella, open Chrome
        #   इला, क्रोम खोलो
        #   एला, क्रोम खोलो
        #
        # A valid boundary is required after the name so that words
        # merely beginning with "ela" are not treated as wake words.
        self.wake_pattern = re.compile(
            r"^\s*"
            r"(?:(?:hello|hey|hi)\s+)?"
            r"(?:ela|ella|aila|ayla|eila|एला|इला|ईला)"
            r"(?=$|[\s,.:;!?-])"
            r"[\s,.:;!?-]*"
            r"(.*)$",
            re.IGNORECASE,
        )

        self.wake_pattern = re.compile(WAKE_WORD_PATTERN, re.IGNORECASE)

        print("Ela is ready.")

    def _extract_wake_command(self, text):
        """Return a command following Ela or an explicit open command ending in AI.

        Returns:
            None: Wake word was not detected.
            "": Wake word was detected without a command.
            str: The command following the wake word.
        """
        if not text:
            return None

        text = text.strip()

        if not text:
            return None

        match = self.wake_pattern.match(text)

        if match:
            return match.group(1).strip()

        # Treat "AI" as a spoken address on a clear open/navigation command,
        # so phrases such as "Open YouTube AI" work in one utterance.
        addressed_command = OPEN_COMMAND_WITH_AI_SUFFIX.match(text)
        if addressed_command:
            return addressed_command.group(1).strip()

        return None

    def _speak(self, text):
        """Speak a non-empty response and handle TTS errors."""
        if not text:
            print("Ela did not generate a response.")
            return

        try:
            self.tts.speak(text)
        except Exception as error:
            print(f"Voice output failed: {type(error).__name__}: {error}")

    def run_once(self):
        """Record and process one speech segment."""
        audio = self.microphone.record()

        if not audio:
            print("No microphone speech captured; check the input device and sensitivity.")
            return

        text = self.stt.transcribe(audio)

        if not text:
            reason = getattr(getattr(self.stt, "last_result", None), "reason", "")
            suffix = f" ({reason})" if reason else ""
            print(f"No speech recognized{suffix}; staying idle.")
            return

        text = text.strip()

        if not text:
            print("Empty transcription; staying idle.")
            return

        # Do not process unreliable speech recognition results.
        last_result = getattr(self.stt, "last_result", None)

        if (
            last_result is not None
            and not getattr(last_result, "reliable", True)
        ):
            print("Speech transcription is unreliable; ignoring it.")
            return

        print(f"Heard: {text}")

        # In standby mode, a wake word is required.
        command = self._extract_wake_command(text)

        if command is not None:
            self.active_until = (
                time.monotonic() + self.wake_timeout_seconds
            )

            if not command:
                print("Wake word detected. Ela is active.")
                self._speak("Haan, bolo.")
                return

            text = command
            print(f"Wake word detected. Command: {text}")

        elif time.monotonic() > self.active_until:
            print("Wake word not detected; ignoring speech.")
            return

        else:
            print("Ela is in active follow-up mode.")

        # Normalize the command for cancellation checks.
        normalized_text = text.lower().strip(" \t\r\n.,!?;:।")

        normalized_text = normalized_text.rstrip("\u0964")

        cancel_phrases = {
            "stop",
            "cancel",
            "ruko",
            "रुको",
            "रुक जाओ",
            "band karo",
            "बंद करो",
            "बस",
        }

        if normalized_text in CANCEL_PHRASES:
            self.active_until = 0.0

            # Cancel pending confirmations/tasks if these interfaces exist.
            try:
                dispatcher = getattr(self.brain, "task_dispatcher", None)

                if dispatcher is not None:
                    confirmation_manager = getattr(
                        dispatcher, "confirmation_manager", None
                    )
                    if confirmation_manager is not None:
                        confirmation_manager.cancel()

                    task_state = getattr(dispatcher, "task_state", None)
                    if task_state is not None:
                        task_state.cancel_active()

            except Exception as error:
                print(
                    "Cancellation cleanup failed: "
                    f"{type(error).__name__}: {error}"
                )

            self._speak("Okay, returning to standby.")
            return

        # Extend the active interaction window for follow-up commands.
        self.active_until = (
            time.monotonic() + self.wake_timeout_seconds
        )

        # Generate a response using Ela's existing brain.
        try:
            response = self.brain.process(text)
        except Exception as error:
            print(
                f"Request processing failed: "
                f"{type(error).__name__}: {error}"
            )
            self._speak("Sorry, I could not process that request.")
            return

        if not isinstance(response, str):
            if response is None:
                response = ""
            else:
                response = str(response)

        response = response.strip()

        if not response:
            print("Ela: No response was generated.")
            self._speak("Sorry, I don't have a response right now.")
            return

        print(f"Ela: {response}")
        self._speak(response)

    def run_forever(self):
        """Continuously listen for speech until interrupted."""
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

                if consecutive_errors >= 3:
                    print("Too many consecutive errors. Ela stopped.")
                    break

                time.sleep(0.5)

        if self.phone_server is not None:
            self.phone_server.stop()


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run_forever()
