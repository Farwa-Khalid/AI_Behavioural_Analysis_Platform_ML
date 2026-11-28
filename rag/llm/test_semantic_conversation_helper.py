from rag.llm.test_adaptive_conversation import (
    get_semantic_evidence,
)


def main():

    response = (
        "My final year project is really stressful. "
        "I keep thinking about the consequences."
    )

    history = [
        {
            "role": "User",
            "text": "I have been struggling with my final year project.",
        },
        {
            "role": "Assistant",
            "text": "What aspects of the project concern you?",
        },
    ]

    result = get_semantic_evidence(
        user_response=response,
        conversation_history=history,
    )

    print("\nSEMANTIC EXTRACTION RESULT")
    print("=" * 60)

    print("Status:", result.get("status"))
    print("Original response:", result.get("original_response"))

    print("\nEvidence:")

    for item in result.get("evidence", []):
        print(item)

    print(
        "\nClarification:",
        result.get("clarification_question"),
    )


if __name__ == "__main__":
    main()