from brain.conversation.context import ConversationContext
from brain.conversation.engine.local_engine import LocalConversationEngine


context = ConversationContext()

engine = LocalConversationEngine(context)


response1 = engine.respond("Hello Ela")
print(f"Ela: {response1}")

response2 = engine.respond("How are you?")
print(f"Ela: {response2}")

print("\nCurrent context:")
print(context.get_messages())

response3 = engine.respond("I am working on my project")
print(f"Ela: {response3}")

response4 = engine.respond("I am building Ela")
print(f"Ela: {response4}")

response5 = engine.respond("What am I working on?")
print(f"Ela: {response5}")

context.clear()

response6 = engine.respond("What am I working on?")
print(f"Ela: {response6}")

response7 = engine.respond("नमस्ते")
print(f"Ela: {response7}")

response8 = engine.respond("कैसे हो?")
print(f"Ela: {response8}")

response9 = engine.respond("Hello Ela")
print(f"Ela: {response9}")

response10 = engine.respond("Hi Ela, kaise ho?")
print(f"Ela: {response10}")