"""
Integration test for:

evidence_extractor.py
        +
assessment_state.py
"""

from rag.assessment.assessment_state import (
    create_assessment_state,
    add_user_response,
    apply_extracted_evidence,
)

from rag.assessment.evidence_extractor import (
    extract_behavioral_evidence,
)


def print_state(state):
    print("\n" + "=" * 60)
    print("CURRENT ASSESSMENT STATE")
    print("=" * 60)

    for construct, attributes in state["constructs"].items():

        detected = attributes.get("detected")

        if detected is not None:
            print(f"\n{construct}:")
            print(f"  detected = {detected}")

            for attribute, value in attributes.items():

                if attribute != "detected" and value is not None:
                    print(f"  {attribute} = {value}")

    print("\n" + "=" * 60)
    print("EVIDENCE HISTORY")
    print("=" * 60)

    for item in state["evidence_history"]:
        print(item)


def main():

    # --------------------------------------------------------
    # 1. Create a new assessment
    # --------------------------------------------------------

    state = create_assessment_state()

    print("Assessment created.")


    # --------------------------------------------------------
    # 2. Simulate a user's response
    # --------------------------------------------------------

    user_response = (
        "I keep worrying that I'll fail my presentation."
    )

    print("\nUSER RESPONSE:")
    print(user_response)


    # --------------------------------------------------------
    # 3. Record the user's response
    # --------------------------------------------------------

    add_user_response(
        state,
        user_response
    )


    # --------------------------------------------------------
    # 4. Extract behavioral evidence
    # --------------------------------------------------------

    extracted_evidence = extract_behavioral_evidence(
        user_response
    )

    print("\nEXTRACTED EVIDENCE:")
    print(extracted_evidence)


    # --------------------------------------------------------
    # 5. Store evidence in assessment state
    # --------------------------------------------------------

    apply_extracted_evidence(
        state=state,
        extracted_evidence=extracted_evidence,
        source_turn=state["conversation"]["turn_count"],
        confidence=0.8,
    )


    # --------------------------------------------------------
    # 6. Display final state
    # --------------------------------------------------------

    print_state(state)


if __name__ == "__main__":
    main()