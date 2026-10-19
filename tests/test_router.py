from router.intent_router.basic_router import BasicIntentRouter


router = BasicIntentRouter()

test_inputs = [
    "Open Safari",
    "Search for today's weather",
    "Call Mom",
    "What is quantum computing?"
]

for text in test_inputs:
    intent = router.route(text)
    print(f"Input: {text}")
    print(f"Intent: {intent}")
    print()