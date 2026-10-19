from brain.llm.llm_escalation import LLMEscalation
from brain.llm.llm_factory import create_llm


llm = create_llm()
escalation = LLMEscalation(llm)

response = escalation.escalate(
    "Explain quantum computing simply.",
    []
)

print("Ela:", response)