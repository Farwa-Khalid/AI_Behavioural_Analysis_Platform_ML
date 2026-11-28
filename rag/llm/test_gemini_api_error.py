
import os
import rag.llm.llm_question_generator as qg


# Simulate a Gemini API failure
class FakeModels:
    def generate_content(self, **kwargs):
        raise RuntimeError("Simulated Gemini API failure")


class FakeClient:
    def __init__(self, api_key):
        self.models = FakeModels()


qg.genai.Client = FakeClient
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

conversation_history = [
    {
        "role": "Assistant",
        "text": (
            "How many times do these worries come up "
            "during a typical day or week?"
        )
    }
]

print("\n========== GEMINI API ERROR TEST ==========")

result = qg.generate_follow_up_question(
    objective=objective,
    retrieved_passages=retrieved_passages,
    conversation_history=conversation_history,
)

print("\nFINAL QUESTION:")
print(result)

print("\nIs final question repetitive?")
print(
    qg.is_question_repetitive(
        result,
        conversation_history,
    )
)

if (
    result
    and not qg.is_question_repetitive(
        result,
        conversation_history,
    )
    and qg.is_question_aligned_with_objective(
        result,
        objective,
    )
):
    print("\nTEST PASSED: API failure fallback works.")
else:
    print("\nTEST FAILED: API failure fallback needs investigation.")
