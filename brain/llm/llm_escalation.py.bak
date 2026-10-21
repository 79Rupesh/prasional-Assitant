from core.interfaces.llm_escalation import LLMEscalationProvider


class LLMEscalation(LLMEscalationProvider):

    def __init__(self, llm):
        self.llm = llm

    def escalate(self, text: str, context: list) -> str:

        context_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in context
        )

        prompt = f"""
You are Ela, a personal AI assistant.

Current conversation:
{context_text}

User's current request:
{text}

Answer naturally and directly.
Do not mention internal architecture, routing, or escalation.
"""

        return self.llm.generate(prompt)