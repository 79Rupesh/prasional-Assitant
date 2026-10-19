from brain.llm.gemini_llm import GeminiLLM


def test_gemini_llm():
    llm = GeminiLLM()

    response = llm.generate("Reply with exactly: Hello from Ela")

    assert response
    print(f"Ela: {response}")