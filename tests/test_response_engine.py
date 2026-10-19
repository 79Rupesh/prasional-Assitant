from brain.conversation.response.response_engine import LocalResponseEngine


engine = LocalResponseEngine()

context = []


tests = [
    ("Tell me something about AI", "english"),
    ("I am working on Ela", "english"),
    ("मुझे एक idea चाहिए", "hindi"),
    ("Mujhe coding karni hai", "hinglish"),
]


for text, language in tests:
    response = engine.generate(
        text,
        language,
        context
    )

    print(f"User: {text}")
    print(f"Ela: {response}")
    print()