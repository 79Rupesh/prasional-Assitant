from brain.brain_coordinator import BrainCoordinator
from brain.conversation.context import ConversationContext
from brain.llm.llm_factory import create_llm


context = ConversationContext()
llm = create_llm()

brain = BrainCoordinator(
    context,
    llm
)


tests = [
    "Hello",
    "How are you?",
    "Tell me something about quantum computing",
]


for text in tests:

    print(f"User: {text}")

    response = brain.process(text)

    print(f"Ela: {response}")
    print()