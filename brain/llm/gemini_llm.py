from google import genai

from core.config.settings import settings
from core.interfaces.llm import LLMProvider


class GeminiLLM(LLMProvider):

    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            if not response.text:
                return "I couldn't generate a response."

            return response.text.strip()

        except Exception as error:
            print(f"LLM Error: {error}")

            return (
                "I'm unable to reach my language model right now."
            )