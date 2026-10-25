from datetime import datetime
import re

from core.interfaces.response_engine import ResponseEngineProvider
from core.interfaces.response_result import ResponseResult
from brain.conversation.intent.detector import ConversationIntentDetector


class LocalResponseEngine(ResponseEngineProvider):

    def __init__(self):
        self.intent_detector = ConversationIntentDetector()

    def generate(
        self,
        text: str,
        language: str,
        context: list
    ) -> ResponseResult:

        # Normalize punctuation for conversation matching
        text_lower = re.sub(
            r"[^\u0900-\u097F\w\s]",
            "",
            text.lower()
        ).strip()

        # Detect conversational intent
        intent = self.intent_detector.detect(text)

        print(f"Conversation intent: {intent}")

        words = text_lower.split()

        if not words:
            return ResponseResult(
                response="I didn't hear anything."
            )

        # Greeting
        if self.is_greeting(text_lower, words):
            return ResponseResult(
                response=self.generate_greeting(language)
            )

        # Status
        if language == "hindi" and "कैसे हो" in text_lower:
            return ResponseResult(
                response="मैं ठीक हूँ Sir। बताइए, आज क्या करना है?"
            )

        if language == "hinglish" and "kaise ho" in text_lower:
            return ResponseResult(
                response="Main bilkul theek hoon Sir. Bataiye, kya karna hai?"
            )

        if "how are you" in text_lower:
            return ResponseResult(
                response="I'm doing well, Sir. What are we working on?"
            )

        # Identity
        if (
            "your name" in text_lower
            or "who are you" in text_lower
            or text_lower in {"आपका नाम क्या है", "तुम्हारा नाम क्या है"}
        ):
            if language == "hindi":
                return ResponseResult(
                    response="मैं एला हूँ, आपकी निजी सहायक।"
                )
            return ResponseResult(
                response="I'm Ela, your personal AI assistant."
            )

        if text_lower in {
            "what can you do",
            "what are your capabilities",
            "how can you help me",
            "what do you do",
            "help",
            "तुम क्या कर सकती हो",
            "आप क्या कर सकती हैं",
        }:
            if language == "hindi":
                return ResponseResult(
                    response=(
                        "मैं बातचीत कर सकती हूँ, सीधे सवालों के जवाब दे "
                        "सकती हूँ और समर्थित डेस्कटॉप कामों में मदद कर सकती हूँ।"
                    )
                )
            return ResponseResult(
                response=(
                    "I can chat, answer straightforward questions, and help "
                    "with supported desktop tasks such as opening apps, "
                    "searching the web, and managing files."
                )
            )

        if text_lower in {
            "what time is it",
            "tell me the time",
            "current time",
            "समय क्या हुआ है",
            "अभी कितने बजे हैं",
        }:
            current_time = datetime.now().strftime("%I:%M %p")
            if language == "hindi":
                return ResponseResult(response=f"अभी {current_time} बजे हैं।")
            return ResponseResult(response=f"It's {current_time}.")

        if text_lower in {
            "what is the date",
            "what is todays date",
            "what day is it",
            "what is today",
            "आज कौन सी तारीख है",
            "आज कौन सा दिन है",
        }:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            if language == "hindi":
                return ResponseResult(response=f"आज {current_date} है।")
            return ResponseResult(response=f"Today is {current_date}.")

        # Gratitude
        if any(
            phrase in text_lower
            for phrase in [
                "thank you",
                "thanks",
                "thank u"
            ]
        ):
            return ResponseResult(
                response="You're welcome, Sir."
            )

        # Acknowledgement
        if self.is_acknowledgement(text_lower):
            return ResponseResult(
                response=self.generate_acknowledgement(language)
            )

        # Time-based greetings
        if "good morning" in text_lower:
            return ResponseResult(
                response="Good morning, Sir. Ready when you are."
            )

        if "good night" in text_lower:
            return ResponseResult(
                response="Good night, Sir."
            )

        # General conversation
        if "what are you doing" in text_lower:
            return ResponseResult(
                response="I'm here and ready for your next task."
            )

        if "are you there" in text_lower:
            return ResponseResult(
                response="Yes, Sir. I'm listening."
            )

        # Context
        if "what am i working on" in text_lower:
            user_messages = [
                message["content"]
                for message in context
                if message["role"] == "user"
            ]

            if len(user_messages) >= 2:
                previous_text = user_messages[-2]

                return ResponseResult(
                    response=(
                        f"You're working on: "
                        f"'{previous_text}'."
                    )
                )

            return ResponseResult(
                response=(
                    "You haven't told me what you're "
                    "working on yet."
                )
            )

        # Emotional / conversational statements
        if intent == "emotional_state":

            if any(
                word in text_lower
                for word in [
                    "tired",
                    "exhausted",
                    "bored"
                ]
            ):
                return ResponseResult(
                    response=(
                        "I understand, Sir. "
                        "Maybe take a short break. "
                        "What would you like to do?"
                    )
                )

            if any(
                word in text_lower
                for word in [
                    "happy",
                    "good",
                    "excited"
                ]
            ):
                return ResponseResult(
                    response=(
                        "Good to hear, Sir. "
                        "What are we doing next?"
                    )
                )

            return ResponseResult(
                response="I understand, Sir."
            )

        # General user statements
        if intent == "personal_statement":

            if (
                text_lower.startswith("i am ")
                or text_lower.startswith("im ")
            ):
                return ResponseResult(
                    response=(
                        "Got it, Sir. "
                        "I'll keep that in mind for this conversation."
                    )
                )

            if text_lower.startswith("mujhe "):
                return ResponseResult(
                    response=(
                        "Samajh gaya, Sir. "
                        "Aage kya karna hai?"
                    )
                )

        # Unknown → LLM
        return ResponseResult(
            response=self.generate_dynamic_fallback(text),
            needs_llm=True
        )

    def is_greeting(
        self,
        text_lower: str,
        words: list
    ) -> bool:

        if any(
            greeting in words
            for greeting in [
                "hello",
                "hi",
                "hey"
            ]
        ):
            return True

        if text_lower in [
            "नमस्ते",
            "नमस्कार"
        ]:
            return True

        return False

    def generate_greeting(self, language: str) -> str:

        if language == "hindi":
            return (
                "नमस्ते Sir। "
                "मैं आपकी मदद के लिए तैयार हूँ।"
            )

        if language == "hinglish":
            return (
                "Hello Sir. "
                "Bataiye, main aapki kya help kar sakti hoon?"
            )

        return "Hello Sir. How can I help you?"

    def is_acknowledgement(
        self,
        text_lower: str
    ) -> bool:

        phrases = [
            "okay",
            "ok",
            "okay thanks",
            "okay no problem",
            "alright",
            "all right",
            "got it",
            "understood",
            "no problem",
            "fine",
            "sure",
            "yes",
            "yeah",
            "yep"
        ]

        return text_lower in phrases

    def generate_acknowledgement(
        self,
        language: str
    ) -> str:

        if language == "hindi":
            return "ठीक है Sir।"

        if language == "hinglish":
            return "Theek hai Sir."

        return "Alright, Sir."

    def generate_dynamic_fallback(
        self,
        text: str
    ) -> str:

        word_count = len(text.split())

        if word_count <= 3:
            return (
                f"I heard you say '{text}'. "
                "What would you like me to do with that?"
            )

        return (
            f"I understand what you said, Sir: "
            f"'{text}'. "
            "Tell me what you'd like to do next."
        )