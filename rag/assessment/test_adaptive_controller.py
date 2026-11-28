"""
Test the adaptive assessment controller.

Flow:

User response
    ↓
Evidence extraction
    ↓
Assessment state
    ↓
Adaptive controller
"""
from rag.assessment.assessment_state import (
    create_assessment_state,
    add_user_response,
    apply_extracted_evidence,
    update_evidence,
)

from rag.assessment.evidence_extractor import (
    extract_behavioral_evidence,
)

from rag.assessment.adaptive_controller import (
    get_next_assessment_objective,
)

def main():

    test_responses = [

        # ----------------------------------------------------
        # Test 1: Worry
        # ----------------------------------------------------
        "I keep worrying that I'll fail my presentation.",


        # ----------------------------------------------------
        # Test 2: Rumination
        # ----------------------------------------------------
        "After something embarrassing happens, I replay it over and over.",


        # ----------------------------------------------------
        # Test 3: Emotional reactivity
        # ----------------------------------------------------
        "I get overwhelmed very easily when I have too much work.",


        # ----------------------------------------------------
        # Test 4: Social evaluation
        # ----------------------------------------------------
        "I constantly worry about what other people think of me.",


        # ----------------------------------------------------
        # Test 5: Negative self-evaluation
        # ----------------------------------------------------
        "I always feel like I'm not good enough.",
    ]


    for test_number, user_response in enumerate(
        test_responses,
        start=1
    ):

        print("\n")
        print("=" * 70)
        print(f"TEST {test_number}")
        print("=" * 70)


        # ------------------------------------------------
        # 1. Create a fresh assessment
        # ------------------------------------------------

        state = create_assessment_state()


        # ------------------------------------------------
        # 2. Display user response
        # ------------------------------------------------

        print("\nUSER:")
        print(user_response)


        # ------------------------------------------------
        # 3. Record response
        # ------------------------------------------------

        add_user_response(
            state,
            user_response
        )


        # ------------------------------------------------
        # 4. Extract behavioral evidence
        # ------------------------------------------------

        evidence = extract_behavioral_evidence(
            user_response
        )

        print("\nEXTRACTED EVIDENCE:")
        print(evidence)


        # ------------------------------------------------
        # 5. Store evidence in assessment state
        # ------------------------------------------------

        apply_extracted_evidence(
            state=state,
            extracted_evidence=evidence,
            source_turn=state["conversation"]["turn_count"],
            confidence=0.8,
        )


        # ------------------------------------------------
        # 6. Ask adaptive controller
        # ------------------------------------------------

        next_objective = get_next_assessment_objective(
            state
        )


        # ------------------------------------------------
        # 7. Display controller decision
        # ------------------------------------------------

        print("\nNEXT OBJECTIVE:")
        print(next_objective)

    # ----------------------------------------------------
    # Test 6: Known trigger, uncertain detection
    # ----------------------------------------------------

    print("\n")
    print("=" * 70)
    print("TEST 6: Known trigger with unconfirmed detection")
    print("=" * 70)

    state = create_assessment_state()

    update_evidence(
        state=state,
        construct="stress_vulnerability",
        attribute="trigger",
        value="final year project",
        evidence_state="known",
        source_turn=1,
        confidence=0.8,
    )

    print("\nSTRESS VULNERABILITY STATE:")
    print(state["constructs"]["stress_vulnerability"])

    next_objective = get_next_assessment_objective(state)

    print("\nNEXT OBJECTIVE:")
    print(next_objective)

    assert (
        state["constructs"]["stress_vulnerability"]["detected"]
        is None
    ), "Detection should remain unconfirmed."

    assert next_objective is not None, (
        "Controller stopped despite having a known trigger."
    )

    assert (
        next_objective["construct"] == "stress_vulnerability"
    ), "Controller selected an unexpected construct."

    print("\nTEST 6 PASSED")
    
if __name__ == "__main__":
    main()