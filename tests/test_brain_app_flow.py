from brain.brain_coordinator import BrainCoordinator
from brain.conversation.context import ConversationContext


context = ConversationContext()

brain = BrainCoordinator(
    context=context,
    llm=None
)


commands = [
    "Open Safari",
    "Launch Calculator",
    "Close Safari",
]


for command in commands:

    print()
    print(f"USER: {command}")

    result = brain.process(command)

    print(f"ELA: {result}")