
"""
Test multi-turn adaptive assessment.

The same assessment state is reused across all turns.
"""

from assessment_state import (
    create_assessment_state,
    add_user_response,
    apply_extracted_evidence,
)

from evidence_extractor import extract_behavioral_evidence

from adaptive_controller import get_next_assessment_objective


def main():
    # 1. Create ONE assessment state for the entire conversation.
    state = create_assessment_state()

    user_responses = [
        "I keep worrying that I'll fail my presentation.",
        "The worry stays with me for hours, and I find it hard to stop thinking about it.",
        "It happens before almost every presentation.",
    ]

    # 2. Process each response using the SAME state.
    for turn_number, user_response in enumerate(user_responses, start=1):
        print("\n" + "=" * 70)
        print(f"TURN {turn_number}")
        print("=" * 70)

        print("\nUSER RESPONSE:")
        print(user_response)

        # Record the response.
        add_user_response(state, user_response)

        # Extract evidence from this response.
        extracted_evidence = extract_behavioral_evidence(user_response)

        print("\nEXTRACTED EVIDENCE:")
        print(extracted_evidence)

        # Update the existing state.
        apply_extracted_evidence(
            state=state,
            extracted_evidence=extracted_evidence,
            source_turn=state["conversation"]["turn_count"],
            confidence=0.8,
        )

        # Select the next objective.
        next_objective = get_next_assessment_objective(state)

        print("\nNEXT ASSESSMENT OBJECTIVE:")
        print(next_objective)

        print("\nCONVERSATION TURNS RECORDED:")
        print(state["conversation"]["turn_count"])

    # 3. Display the final state.
    print("\n" + "=" * 70)
    print("FINAL ASSESSMENT SUMMARY")
    print("=" * 70)

    print("\nWORRY EVIDENCE:")
    print(state["constructs"]["worry"])

    print("\nCONVERSATION HISTORY:")
    for response in state["conversation"]["recent_responses"]:
        print(response)

    print("\nEVIDENCE HISTORY:")
    for item in state["evidence_history"]:
        print(item)


if __name__ == "__main__":
    main()