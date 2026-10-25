
from openai import OpenAI

from core.config.settings import settings
from core.interfaces.llm import LLMProvider


class OpenAILLM(LLMProvider):

    def __init__(self):
        provider = settings.llm_provider.lower()
        client_options = {
            "timeout": 30.0,
            "max_retries": 0,
        }

        if provider == "openrouter":
            if not settings.openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY is not configured.")
            client_options["api_key"] = settings.openrouter_api_key
            client_options["base_url"] = "https://openrouter.ai/api/v1"
            self.model = settings.openrouter_model
        elif provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not configured.")
            client_options["api_key"] = settings.openai_api_key
            self.model = settings.openai_model
        else:
            raise ValueError(f"Unsupported OpenAI-compatible provider: {provider}")

        self.client = OpenAI(**client_options)

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
        
        if response is None:
            raise RuntimeError("LLM provider returned no response.")

        if not response.choices:
            raise RuntimeError("LLM provider returned no choices.")

        content = response.choices[0].message.content

        if not content:
            return "I couldn't generate a response."

        return content.strip()
