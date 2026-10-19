from core.interfaces.language_detector import LanguageDetectorProvider


class LanguageDetector(LanguageDetectorProvider):

    def detect(self, text: str) -> str:
        text = text.strip().lower()

        if not text:
            return "unknown"

        hindi_chars = sum(
            1 for char in text
            if "\u0900" <= char <= "\u097f"
        )
        

        english_chars = sum(
            1 for char in text
            if "a" <= char <= "z"
        )

        total_letters = hindi_chars + english_chars

        if total_letters == 0:
            return "unknown"

        hindi_ratio = hindi_chars / total_letters

        if hindi_ratio > 0.5:
            return "hindi"

        hinglish_words = [
            "kya",
            "kaise",
            "ho",
            "hai",
            "hain",
            "mera",
            "meri",
            "aap",
            "aapki",
            "mujhe",
            "mujhse",
            "kar",
            "raha",
            "rahi",
            "rahe",
            "batao",
            "bataiye",
            "chahiye",
            "nahi",
            "haan",
            "theek"
        ]

        words = text.split()

        if any(word in hinglish_words for word in words):
            return "hinglish"
        

        if hindi_ratio > 0:
            return "hinglish"

        return "english"