
from rag.llm.llm_question_generator import (
    generate_follow_up_question,
)


objective = (
    "Assess how difficult it is for the person "
    "to stop or control worry."
)

retrieved_passages = [
    {
        "source": "worry_future_threat.md",
        "content": (
            "Worry involves repeated thoughts about possible "
            "future threats. An important aspect is how "
            "difficult these thoughts are to control or stop."
        ),
    }
]

question = generate_follow_up_question(
    objective,
    retrieved_passages,
)

print("\nGenerated assessment question:")
print(question)
