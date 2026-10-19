from core.interfaces.conversation_context import ConversationContextProvider
from brain.conversation.language.detector import LanguageDetector
from brain.conversation.response.response_engine import LocalResponseEngine
from brain.llm.llm_escalation import LLMEscalation
from brain.task.local_classifier import LocalTaskClassifier
from actions.task_dispatcher import TaskDispatcher


class BrainCoordinator:

    def __init__(
        self,
        context: ConversationContextProvider,
        llm
        
    ):
        self.context = context

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

        text = text.strip()

        if not text:
            return "I didn't hear anything."

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
            response = self.llm_escalation.escalate(
                text,
                self.context.get_messages()
            )

            if not response or not response.strip():
                response = "Sorry Sir, I couldn't generate a response. Please try again."

        except Exception as error:
            print(
                f"LLM escalation failed: "
                f"{type(error).__name__}: {error}"
            )

            response = (
                "Sorry Sir, my response service is unavailable right now. "
                "Please try again."
            )

        self.context.add_message(
            "assistant",
            response
        )

        return response