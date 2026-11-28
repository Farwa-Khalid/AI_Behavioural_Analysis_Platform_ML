import re


def check_safeguard(response):
    has_repeated_pattern = bool(
        re.search(
            r"\b(every day|daily|often|frequently|regularly|repeatedly|all the time|most of the time|keeps happening|whenever I face|whenever I experience)\b",
            response,
            re.IGNORECASE,
        )
    )

    has_general_coping_difficulty = bool(
        re.search(
            r"\b(struggle|struggling|have difficulty|find it difficult|find it hard|unable|cannot|can't)\b.{0,50}\b(cope|coping|manage|managing|handling|handle|recover)\b|\b(difficulty|difficulties)\b.{0,35}\b(coping|managing|handling|recovering)\b",
            response,
            re.IGNORECASE,
        )
    )

    return (
        has_repeated_pattern
        and has_general_coping_difficulty
    )


test_responses = [
    "My final year project is really stressful.",
    "I have meetings every day.",
    "I struggle to cope with this project.",
    "I often struggle to cope with stressful situations.",
    "I am frequently overwhelmed by my workload.",
    "I regularly have difficulty managing stress.",
]

for response in test_responses:
    print("\nResponse:", response)
    print("Safeguard allows known:", check_safeguard(response))