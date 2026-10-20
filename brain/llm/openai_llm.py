
from openai import OpenAI

from core.config.settings import settings
from core.interfaces.llm import LLMProvider


class OpenAILLM(LLMProvider):

    def __init__(self):
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        self.model = "xingchen-agi/xing4.0-29b-a4b:free"

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        
        print("OpenRouter response:", repr(response))

        if response is None:
            raise RuntimeError("OpenRouter returned no response.")

        if not response.choices:
            raise RuntimeError(
                f"OpenRouter returned no choices. Response: {response!r}"
            )

        content = response.choices[0].message.content

        if not content:
            return "I couldn't generate a response."

        return content.strip()
