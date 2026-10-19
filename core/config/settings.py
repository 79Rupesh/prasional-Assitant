import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self):
        self.environment = os.getenv("ELA_ENV", "development")
        self.llm_provider = os.getenv("LLM_PROVIDER", "gemini")

        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.stt_api_key = os.getenv("STT_API_KEY")
        self.tts_api_key = os.getenv("TTS_API_KEY")

        self.ela_pin = os.getenv("ELA_PIN")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")


settings = Settings()