
import os
import rag.llm.llm_question_generator as qg


# Simulate a valid Gemini response
class FakeResponse:
    text = "How often do these worries occur in your everyday life?"


class FakeModels:
    def generate_content(self, **kwargs):
        return FakeResponse()


class FakeClient:
    def __init__(self, api_key):
        self.models = FakeModels()


# Replace Gemini with our fake client
qg.genai.Client = FakeClient

# Provide a test API key
os.environ["GEMINI_API_KEY"] = "test_key"


objective = {
    "construct": "worry",
    "attribute": "frequency",
    "priority": 4,
    "objective": "Determine how often these worries occur."
}

retrieved_passages = [
    {
        "source": "worry.md",
        "content": (
            "Worry involves repeated thoughts about possible "
            "future problems or uncertain outcomes."
        )
    }
]

print("\n========== VALID GEMINI RESPONSE TEST ==========")

result = qg.generate_follow_up_question(
    objective=objective,
    retrieved_passages=retrieved_passages,
)

print("\nFINAL QUESTION:")
print(result)

expected = FakeResponse.text

if result == expected:
    print("\nTEST PASSED: Valid Gemini question was accepted.")
else:
    print("\nTEST FAILED: Gemini question was not accepted.")
