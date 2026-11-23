
from rag.assessment.adaptive_controller import (
    get_next_assessment_objective,
)
from rag.llm.llm_question_generator import (
    generate_follow_up_question,
)


# Simulated state: worry has already been detected.
state = {
    "constructs": {
        "worry": {
            "detected": True,
            "temporal_orientation": None,
            "trigger": None,
            "content": None,
            "frequency": None,
            "intensity": None,
            "persistence": None,
            "controllability": None,
            "switching_difficulty": None,
            "functional_impact": None,
            "recovery": None,
            "repetition": None,
        }
    }
}


# 1. Controller decides what evidence is missing.
objective = get_next_assessment_objective(state)

if objective is None:
    print("No additional evidence is required.")
    raise SystemExit

print("CONTROLLER OBJECTIVE:")
print(objective)


# 2. Retrieve relevant knowledge passages.
from rag.retrieval.semantic_retriever import (
    retrieve_semantic_passages,
)

passages = retrieve_semantic_passages(
    objective["objective"],
    top_k=3,
)

print("\nRETRIEVED SOURCES:")
for passage in passages:
    print("-", passage["source"])


# 3. Gemini generates the question.
question = generate_follow_up_question(
    objective["objective"],
    passages,
)

print("\nGENERATED QUESTION:")
print(question)
