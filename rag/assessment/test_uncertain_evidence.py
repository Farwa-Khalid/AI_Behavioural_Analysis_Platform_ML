
from rag.assessment.assessment_state import (
    create_assessment_state,
    update_evidence,
    get_evidence,
    get_uncertain_attributes,
)

from rag.assessment.adaptive_controller import (
    get_next_assessment_objective,
)


def main():

    state = create_assessment_state()

    # TEST 1: Establish worry and temporal orientation.

    update_evidence(
        state,
        "worry",
        "detected",
        True,
        evidence_state="known",
        source_turn=1,
        confidence=0.95,
    )

    update_evidence(
        state,
        "worry",
        "temporal_orientation",
        "future",
        evidence_state="known",
        source_turn=1,
        confidence=0.95,
    )

    print("TEST 1 - KNOWN EVIDENCE")
    print("Worry detected:", get_evidence(state, "worry", "detected"))
    print(
        "Temporal orientation:",
        get_evidence(state, "worry", "temporal_orientation"),
    )

    # TEST 2: Add uncertain frequency evidence.

    update_evidence(
        state,
        "worry",
        "frequency",
        "often",
        evidence_state="uncertain",
        source_turn=2,
        confidence=0.55,
    )
    update_evidence(
        state,
        "worry",
        "content",
        "fear of presentation failure",
        evidence_state="known",
        source_turn=1,
        confidence=0.95,
    )

    update_evidence(
        state,
        "worry",
        "repetition",
        True,
        evidence_state="known",
        source_turn=1,
        confidence=0.95,
    )

    print("\nTEST 2 - UNCERTAIN EVIDENCE")
    print("Stored worry frequency:", get_evidence(state, "worry", "frequency"))
    print("Uncertain records:", get_uncertain_attributes(state))

    # TEST 3: Check the controller's next objective.

    objective = get_next_assessment_objective(state)

    print("\nTEST 3 - ADAPTIVE CONTROLLER")
    print("Next objective:", objective)

    if (
        objective is not None
        and objective.get("construct") == "worry"
        and objective.get("attribute") == "frequency"
    ):
        print("\nPASS: Uncertain frequency was not treated as established evidence.")
    else:
        print("\nCHECK: Controller selected a different objective.")


if __name__ == "__main__":
    main()
