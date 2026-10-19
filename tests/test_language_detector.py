from brain.conversation.language.detector import LanguageDetector


detector = LanguageDetector()


tests = [
    "Hello Ela",
    "नमस्ते एला",
    "Hello एला",
    "How are you?",
    "मैं ठीक हूँ"
]


for text in tests:
    language = detector.detect(text)
    print(f"Text: {text}")
    print(f"Language: {language}")
    print()