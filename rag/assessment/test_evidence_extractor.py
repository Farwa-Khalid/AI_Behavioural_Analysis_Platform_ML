
from rag.assessment.evidence_extractor import (
    extract_behavioral_evidence,
)
from rag.assessment.evidence_extractor import (
    extract_contextual_answer,
)

test_cases = [
    (
    "I do worry but not too much",
    True,
    None,
),
    (
        "I feel overwhelmed by my workload",
        None,
        True,
    ),
    (
        "I struggle to cope with multiple deadlines",
        None,
        True,
    ),
]


for text, expected_worry, expected_stress in test_cases:
    result = extract_behavioral_evidence(text)

    worry_detected = result.get("worry", {}).get("detected")
    stress_detected = result.get(
        "stress_vulnerability", {}
    ).get("detected")

    print("\nInput:", text)
    print("Worry detected:", worry_detected)
    print("Stress detected:", stress_detected)

    assert worry_detected is expected_worry, (
        f"Unexpected worry detection for: {text}"
    )

    assert stress_detected is expected_stress, (
        f"Unexpected stress detection for: {text}"
    )

print("\nAll evidence extraction tests passed.")

# Persistence follow-up tests

persistence_objective = {
    "construct": "worry",
    "attribute": "persistence",
}

persistence_cases = [
    ("for sometime", "brief"),
    ("for a while", "brief"),
    ("1 hour may be", "hours"),
    ("last for entire hr", "hours"),
    ("2 days may be", "days"),
    ("I can't specify the time", "uncertain"),
    ("it varies", "variable"),
]

for answer, expected in persistence_cases:
    result = extract_contextual_answer(
        answer,
        persistence_objective,
    )

    actual = result.get("worry", {}).get("persistence")

    print(
        f"Answer: {answer!r} | "
        f"Expected: {expected} | Actual: {actual}"
    )

    assert actual == expected, (
        f"Persistence extraction failed for {answer!r}"
    )

print("All persistence tests passed.")

# ============================================================
# Emotional intensity follow-up tests
# ============================================================

intensity_objective = {
    "construct": "emotional_reactivity",
    "attribute": "intensity",
}

intensity_cases = [
    ("It is distressing and makes me so upset.", "high"),
    ("I feel extremely overwhelmed.", "high"),
    ("It is moderately upsetting.", "moderate"),
    ("It bothers me a little.", "low"),
    ("I feel slightly disturbed.", "low"),
]

for answer, expected in intensity_cases:
    result = extract_contextual_answer(
        answer,
        intensity_objective,
    )

    actual = result.get(
        "emotional_reactivity", {}
    ).get("intensity")

    print(
        f"Answer: {answer!r} | "
        f"Expected: {expected} | Actual: {actual}"
    )

    assert actual == expected, (
        f"Intensity extraction failed for {answer!r}"
    )

print("All intensity tests passed.")

# ============================================================
# Negative and qualified intensity tests
# ============================================================

intensity_edge_cases = [
    ("I don't feel overwhelmed.", None),
    ("I'm not overwhelmed.", None),
    ("I'm not that upset.", "low"),
    ("Sometimes I feel overwhelmed.", "high"),
    ("I feel upset, but only a little.", "low"),
]

for answer, expected in intensity_edge_cases:
    result = extract_contextual_answer(
        answer,
        intensity_objective,
    )

    actual = result.get(
        "emotional_reactivity", {}
    ).get("intensity")

    print(
        f"Answer: {answer!r} | "
        f"Expected: {expected} | Actual: {actual}"
    )

    assert actual == expected, (
        f"Intensity edge case failed for {answer!r}"
    )

print("All intensity edge-case tests passed.")