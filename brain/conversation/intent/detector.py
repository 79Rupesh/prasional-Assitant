from core.interfaces.conversation_intent import ConversationIntentProvider


class ConversationIntentDetector(ConversationIntentProvider):

    def detect(self, text: str) -> str:

        text_lower = text.lower().strip()

        # Emotional state
        emotional_words = [
            "tired",
            "exhausted",
            "bored",
            "happy",
            "sad",
            "angry",
            "upset",
            "excited",
            "lonely",
            "stressed",
            "worried",
        ]

        if any(word in text_lower for word in emotional_words):
            return "emotional_state"

        # Personal statement
        if (
            text_lower.startswith("i am ")
            or text_lower.startswith("im ")
            or text_lower.startswith("i feel ")
            or text_lower.startswith("mujhe ")
        ):
            return "personal_statement"

        # Opinion
        if any(
            phrase in text_lower
            for phrase in [
                "what do you think",
                "what's your opinion",
                "your opinion",
                "do you think",
            ]
        ):
            return "opinion"

        # Question
        if (
            text_lower.startswith("why ")
            or text_lower.startswith("how ")
            or text_lower.startswith("what ")
            or text_lower.startswith("when ")
            or text_lower.startswith("where ")
            or text_lower.startswith("who ")
        ):
            return "question"

        return "general"