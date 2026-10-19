from core.config.settings import settings
from core.interfaces.llm import LLMProvider
from brain.llm.gemini_llm import GeminiLLM
from brain.llm.openai_llm import OpenAILLM


def create_llm() -> LLMProvider:
    provider = settings.llm_provider.lower()

    if provider == "openrouter":
        return OpenAILLM()

    if provider == "gemini":
        return GeminiLLM()

    if provider == "openai":
        return OpenAILLM()

    raise ValueError(f"Unsupported LLM provider: {provider}")