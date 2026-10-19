from core.interfaces.conversation_context import ConversationContextProvider
from brain.conversation.language.detector import LanguageDetector
from brain.conversation.response.response_engine import LocalResponseEngine


class LocalConversationEngine:

    def __init__(self, context: ConversationContextProvider):
        self.context = context
        self.language_detector = LanguageDetector()
        self.response_engine = LocalResponseEngine()

    def respond(self, text: str) -> str:
        text = text.strip()

        if not text:
            return "I didn't hear anything."

        language = self.language_detector.detect(text)

        print(f"Detected language: {language}")

        self.context.add_message("user", text)

        result = self.response_engine.generate(
            text,
            language,
            self.context.get_messages()
        )

        self.context.add_message(
            "assistant",
            result.response
        )

        return result.response