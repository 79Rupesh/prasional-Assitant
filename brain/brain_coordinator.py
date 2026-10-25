import logging
import re
import threading

from brain.knowledge.knowledge_loader import KnowledgeLoader
from core.interfaces.conversation_context import ConversationContextProvider
from brain.conversation.language.detector import LanguageDetector
from brain.conversation.response.response_engine import LocalResponseEngine
from brain.llm.llm_escalation import LLMEscalation
from brain.task.local_classifier import LocalTaskClassifier
from actions.task_dispatcher import TaskDispatcher
from brain.task.voice_command_normalizer import normalize_voice_command


logger = logging.getLogger(__name__)


class BrainCoordinator:

    def __init__(
        self,
        context: ConversationContextProvider,
        llm
        
    ):
        self.context = context
        self._process_lock = threading.RLock()

        self.knowledge_loader = KnowledgeLoader()

        try:
            self.knowledge_loader.load()
            print("Ela knowledge loaded successfully.")
        except (OSError, ValueError) as error:
            self.knowledge_loader = None
            print(f"Knowledge unavailable: {error}")

        self.classifier = LocalTaskClassifier()
        self.language_detector = LanguageDetector()
        self.response_engine = LocalResponseEngine()

        self.llm = llm

        if llm is not None:
            self.llm_escalation = LLMEscalation(llm)
        else:
            self.llm_escalation = None

        self.task_dispatcher = TaskDispatcher(
            context=self.context
        )

    def process(self, text: str) -> str:
        # Local microphone commands and remote phone commands share one desktop.
        # Serialize them so two requests cannot click/type at the same time.
        with self._process_lock:
            return self._process_locked(text)

    def _process_locked(self, text: str) -> str:

        text = text.strip()

        if not text:
            return "I didn't hear anything."

        text = normalize_voice_command(text)

         # Handle pending confirmation before task classification
        if self.task_dispatcher.confirmation_manager.has_pending():

            return self.task_dispatcher.dispatch(
                "confirmation",
                text
            )
       
        if self.task_dispatcher.file_selection_context.get_results():

            return self.task_dispatcher.dispatch(
                "file_task",
                text
            )

        steps = self._split_task_sequence(text)
        if steps:
            return self.task_dispatcher.execute_plan(steps)

        task_type = self.classifier.classify(text)

        print(f"Task type: {task_type}")

        # Direct task
        if task_type != "conversation":

            result = self.task_dispatcher.dispatch(
                task_type,
                text
            )

            return result

        # Conversation
        language = self.language_detector.detect(text)

        self.context.add_message(
            "user",
            text
        )

        result = self.response_engine.generate(
            text,
            language,
            self.context.get_messages()
        )

        # Local response
        if not result.needs_llm:

            self.context.add_message(
                "assistant",
                result.response
            )

            return result.response

        # Complex reasoning → LLM
        if self.llm_escalation is None:

            fallback = (
                "I can handle simple conversations locally, "
                "but my advanced reasoning system is not available right now."
            )

            self.context.add_message(
                "assistant",
                fallback
            )

            return fallback

        try:
            knowledge = ""

            if self.knowledge_loader is not None:
                knowledge = (
                    self.knowledge_loader.get_relevant_sections(
                        text,
                        max_chars=6000
                    )
                )

            response = self.llm_escalation.escalate(
                text,
                self.context.get_messages(),
                knowledge=knowledge
            )

            
        except Exception as error:
            logger.exception("LLM escalation failed")
            if self._is_rate_limit_error(error):
                response = (
                    "Sorry Sir, the language model provider is rate-limited "
                    "or its quota is exhausted. Please wait or check the "
                    "provider quota and try again."
                )
            else:
                response = (
                    "Sorry Sir, my response service is unavailable right now. "
                    "Please try again."
                )

        self.context.add_message(
            "assistant",
            response
        )

        return response

    @staticmethod
    def _is_rate_limit_error(error: Exception) -> bool:
        status_code = getattr(error, "status_code", None)
        error_code = str(getattr(error, "code", "")).lower()
        message = str(error).lower()
        return (
            type(error).__name__ == "RateLimitError"
            or status_code == 429
            or error_code == "429"
            or "resource_exhausted" in error_code
            or "resource_exhausted" in message
            or "quota" in message
            or "rate limit" in message
            or "rate_limit" in message
        )

    def _split_task_sequence(self, text: str):
        """Recognize a short, explicit sequence and execute its steps in order."""
        separators = re.compile(
            r"\s+(?:and\s+then|then|aur\s+phir|phir|और\s+फिर|फिर)\s+",
            re.IGNORECASE,
        )
        raw_steps = [part.strip(" ,.") for part in separators.split(text) if part.strip(" ,.")]
        if len(raw_steps) < 2:
            hindi_separators = re.compile(
                r"\s+(?:\u0914\u0930\s+\u092b\u093f\u0930|\u092b\u093f\u0930)\s+",
                re.IGNORECASE,
            )
            raw_steps = [
                part.strip(" ,.")
                for part in hindi_separators.split(text)
                if part.strip(" ,.")
            ]
        if len(raw_steps) < 2:
            raw_steps = re.split(
                r"\s+and\s+(?=(?:copy|send|open|close|search|play|find|delete|move|rename|click|type|press)\b)",
                text,
                flags=re.IGNORECASE,
            )
            raw_steps = [part.strip(" ,.") for part in raw_steps if part.strip(" ,.")]
        if len(raw_steps) < 2 or len(raw_steps) > 5:
            return []

        plan = []
        for raw in raw_steps:
            command = normalize_voice_command(raw)
            task_type = self.classifier.classify(command)
            if task_type in {"conversation", "unknown"}:
                return []
            plan.append((task_type, command))
        return plan
