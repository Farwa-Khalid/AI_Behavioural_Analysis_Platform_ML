
import os

import rag.llm.llm_question_generator as qg


# Simulate Gemini returning an incorrect trigger question.
class FakeResponse:
    text = "What kinds of situations tend to spark these reactions?"


class FakeModels:
    def generate_content(self, **kwargs):
        return FakeResponse()


class FakeClient:
    def __init__(self, api_key):
        self.models = FakeModels()


# Replace the real Gemini client with our test client.
qg.genai.Client = FakeClient

# Provide a test API key.
os.environ["GEMINI_API_KEY"] = "test_key"


objective = {
    "construct": "emotional_reactivity",
    "attribute": "sensitivity",
    "priority": 11,
    "objective": (
        "Determine how easily the person experiences "
        "strong emotional reactions."
    ),
}

retrieved_passages = [
    {
        "source": "emotional_reactivity.md",
        "content": "Emotional sensitivity describes how readily "
                   "a person responds to emotional situations."
    }
]


result = qg.generate_follow_up_question(
    objective=objective,
    retrieved_passages=retrieved_passages,
)

print("\nFINAL QUESTION:")
print(result)
