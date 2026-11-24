
from rag.llm.llm_question_generator import (
    generate_follow_up_question,
)

from rag.llm.llm_question_generator import (
            is_question_aligned_with_objective,
        )
     
test_cases = [
    {
        "construct": "emotional_reactivity",
        "attribute": "controllability",
        "objective": (
            "Assess how difficult it is to manage "
            "emotional reactions."
        ),
        "passage": (
            "Emotional reactivity involves strong emotional "
            "responses and the ability to regulate them."
        ),
    },
    {
        "construct": "emotional_reactivity",
        "attribute": "intensity",
        "objective": (
            "Assess how strong or distressing emotional "
            "reactions become."
        ),
        "passage": (
            "Emotional intensity describes the strength "
            "of an emotional response."
        ),
    },
    {
        "construct": "worry",
        "attribute": "controllability",
        "objective": (
            "Assess how difficult it is to control worries."
        ),
        "passage": (
            "Worry involves repeated thoughts about possible "
            "future threats and difficulty controlling them."
        ),
    },
    {
        "construct": "rumination",
        "attribute": "repetition",
        "objective": (
            "Assess whether the same thoughts repeatedly return."
        ),
        "passage": (
            "Rumination involves repeatedly thinking about "
            "experiences or concerns."
        ),
    },
    {
        "construct": "stress_vulnerability",
        "attribute": "trigger",
        "objective": (
            "Identify situations that bring about stress-related "
            "responses."
        ),
        "passage": (
            "Stress responses can occur in reaction to "
            "challenging or demanding situations."
        ),
    },
]


for index, test in enumerate(test_cases, start=1):

    objective = {
        "construct": test["construct"],
        "attribute": test["attribute"],
        "objective": test["objective"],
    }

    retrieved_passages = [
        {
            "source": f"test_source_{index}.md",
            "content": test["passage"],
        }
    ]

    print("\n" + "=" * 60)
    print(f"TEST {index}")
    print("Construct:", test["construct"])
    print("Attribute:", test["attribute"])

    question = generate_follow_up_question(
        objective,
        retrieved_passages,
    )

    print("\nGenerated question:")
    print(question)
       

    is_aligned = is_question_aligned_with_objective(
            question,
            objective
        )

    print("Alignment result:", is_aligned)
    print("=" * 60)

print("\n" + "=" * 60)
print("FALLBACK VALIDATION TESTS")
print("=" * 60)

from rag.llm.llm_question_generator import (
    generate_fallback_question,
    is_question_aligned_with_objective,
)

fallback_tests = [
    ("emotional_reactivity", "controllability"),
    ("worry", "frequency"),
    ("rumination", "repetition"),
    ("stress_vulnerability", "trigger"),
    ("negative_self_evaluation", "intensity"),
]

passed = 0

for construct, attribute in fallback_tests:

    objective = {
        "construct": construct,
        "attribute": attribute,
        "objective": "Test objective.",
    }

    question = generate_fallback_question(objective)

    aligned = is_question_aligned_with_objective(
        question,
        objective,
    )

    if aligned:
        passed += 1

    print(f"\nConstruct: {construct}")
    print(f"Attribute: {attribute}")
    print(f"Question: {question}")
    print(f"Alignment: {aligned}")

print("\nFallback validation:", passed, "/", len(fallback_tests))