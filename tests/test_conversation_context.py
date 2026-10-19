from brain.conversation.context import ConversationContext


context = ConversationContext()

context.add_message("user", "Hello Ela")
context.add_message("assistant", "Hello Sir")

print("Messages:")
print(context.get_messages())

context.clear()

print("After clear:")
print(context.get_messages())