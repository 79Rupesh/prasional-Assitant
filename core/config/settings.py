import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self):
        self.environment = os.getenv("ELA_ENV", "development")
        self.llm_provider = os.getenv("LLM_PROVIDER", "gemini")
        wake_timeout = os.getenv("ELA_WAKE_TIMEOUT_SECONDS", "45")
        try:
            self.wake_timeout_seconds = float(wake_timeout)
        except ValueError as error:
            raise ValueError(
                "ELA_WAKE_TIMEOUT_SECONDS must be a number between 5 and 300."
            ) from error
        if not 5 <= self.wake_timeout_seconds <= 300:
            raise ValueError(
                "ELA_WAKE_TIMEOUT_SECONDS must be between 5 and 300."
            )

        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.stt_api_key = os.getenv("STT_API_KEY")
        self.tts_api_key = os.getenv("TTS_API_KEY")

        self.ela_pin = os.getenv("ELA_PIN")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")


settings = Settings()