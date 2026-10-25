import threading
from unittest.mock import MagicMock, patch

from brain.brain_coordinator import BrainCoordinator
from brain.conversation.response.response_engine import LocalResponseEngine
from brain.llm.openai_llm import OpenAILLM
from core.config.settings import settings
from core.interfaces.response_result import ResponseResult


class RateLimitError(Exception):
    status_code = 429


class SimpleContext:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        return self.messages


def conversation_brain(llm_error):
    brain = BrainCoordinator.__new__(BrainCoordinator)
    brain._process_lock = threading.RLock()
    brain.context = SimpleContext()
    brain.task_dispatcher = MagicMock()
    brain.task_dispatcher.confirmation_manager.has_pending.return_value = False
    brain.task_dispatcher.file_selection_context.get_results.return_value = None
    brain.classifier = MagicMock()
    brain.classifier.classify.return_value = "conversation"
    brain.language_detector = MagicMock()
    brain.language_detector.detect.return_value = "english"
    brain.response_engine = MagicMock()
    brain.response_engine.generate.return_value = ResponseResult(
        response="Thinking...", needs_llm=True
    )
    brain.knowledge_loader = None
    brain.llm_escalation = MagicMock()
    brain.llm_escalation.escalate.side_effect = llm_error
    return brain


def test_rate_limit_returns_clear_message_and_logs_full_error(caplog):
    error = RateLimitError("provider quota exceeded")
    brain = conversation_brain(error)

    response = brain.process("Explain a difficult topic")

    assert "rate-limited or its quota is exhausted" in response
    assert "provider quota exceeded" in caplog.text
    assert brain.context.messages[-1]["content"] == response


def test_simple_questions_are_answered_locally_without_llm():
    engine = LocalResponseEngine()

    for text in ("Hello", "How are you?", "What time is it?", "What can you do?"):
        result = engine.generate(text, "english", [])
        assert result.response
        assert not result.needs_llm

    hindi_result = engine.generate("समय क्या हुआ है", "hindi", [])
    assert hindi_result.response
    assert not hindi_result.needs_llm


def test_openrouter_and_openai_use_their_own_key_and_model_settings():
    with patch("brain.llm.openai_llm.OpenAI") as openai_client:
        with patch.object(settings, "llm_provider", "openrouter"):
            with patch.object(settings, "openrouter_api_key", "router-test-key"):
                with patch.object(settings, "openrouter_model", "router-model"):
                    router = OpenAILLM()

        router_options = openai_client.call_args.kwargs
        assert router_options["api_key"] == "router-test-key"
        assert router_options["base_url"] == "https://openrouter.ai/api/v1"
        assert router.model == "router-model"

        with patch.object(settings, "llm_provider", "openai"):
            with patch.object(settings, "openai_api_key", "openai-test-key"):
                with patch.object(settings, "openai_model", "openai-model"):
                    direct = OpenAILLM()

        direct_options = openai_client.call_args.kwargs
        assert direct_options["api_key"] == "openai-test-key"
        assert "base_url" not in direct_options
        assert direct.model == "openai-model"
