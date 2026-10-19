from brain.llm.gemini_llm import GeminiLLM


llm = GeminiLLM()

response = llm.generate("Reply with exactly: Hello from Ela")

print(f"Ela: {response}")