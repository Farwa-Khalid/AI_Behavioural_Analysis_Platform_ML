from unittest.mock import patch

import rag.llm.test_adaptive_conversation as conversation


def fake_semantic_extractor(
    user_response,
    conversation_context=None,
):
    print("\nCONTEXT RECEIVED BY SEMANTIC EXTRACTOR:")
    print(conversation_context)

    return {
        "status": "ok",
        "original_response": user_response,
        "evidence": [
            {
                "construct": "stress_vulnerability",
                "attribute": "detected",
                "value": True,
                "evidence_state": "uncertain",
                "evidence_text": "My final year project is really stressful.",
            }
        ],
        "clarification_question": (
            "Does this kind of stress happen repeatedly "
            "in your life?"
        ),
    }


def main():

    response = (
        "My final year project is really stressful."
    )

    history = [
        {
            "role": "User",
            "text": "I have been struggling with my project.",
        },
        {
            "role": "Assistant",
            "text": "What aspects concern you?",
        },
    ]

    with patch.object(
        conversation,
        "extract_semantic_evidence",
        side_effect=fake_semantic_extractor,
    ):

        result = conversation.get_semantic_evidence(
            response,
            history,
        )

    print("\nMOCK SEMANTIC EXTRACTION RESULT")
    print("=" * 60)

    print("Status:", result["status"])
    print("Original response:", result["original_response"])
    print("Evidence:", result["evidence"])
    print("Clarification:", result["clarification_question"])

    assert result["status"] == "ok"
    assert result["original_response"] == response
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["evidence_state"] == "uncertain"

    print("\nPASS: Successful semantic extraction was handled correctly.")


if __name__ == "__main__":
    main()