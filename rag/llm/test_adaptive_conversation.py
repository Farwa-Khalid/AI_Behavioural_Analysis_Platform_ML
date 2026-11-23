
"""
Multi-Turn Adaptive Conversation Test

Responsibilities:
1. Receive the user's concern or answer.
2. Extract evidence relevant to the current assessment objective.
3. Update the existing assessment state.
4. Limit repeated attempts when an answer is unclear.
5. Skip unanswered attributes without treating them as False.
6. Retrieve relevant knowledge and generate the next question.
7. Stop when the user exits or no objectives remain.
"""

import re

from rag.assessment.assessment_state import (
    create_assessment_state,
    add_user_response,
    apply_extracted_evidence,
    update_conversation_topic,
)

from rag.assessment.evidence_extractor import (
    extract_behavioral_evidence,
    extract_contextual_answer,
)

from rag.assessment.adaptive_controller import (
    get_next_assessment_objective,
)

from rag.retrieval.semantic_retriever import (
    retrieve_semantic_passages,
)

from rag.llm.llm_question_generator import (
    generate_follow_up_question,
)


# Maximum number of unclear answers allowed per objective.
MAX_UNCLEAR_ATTEMPTS = 2


def normalize_text(text):
    """Normalize text for consistent phrase matching."""

    if not isinstance(text, str):
        return ""

    text = text.lower().replace("’", "'")
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def is_conversation_complaint(text):
    """Recognize frustration about repeated or misunderstood questions."""

    normalized = normalize_text(text)

    complaint_patterns = [
        "why are you asking",
        "why you're asking",
        "why youre asking",
        "asking same thing again",
        "asking the same question",
        "same question again",
        "you keep asking",
        "i told you",
        "i already told you",
        "i told you already",
        "i never said",
        "i didn't say",
        "i didnt say",
        "when did i tell you",
        "are you serious",
        "what are you talking about",
        "that's not what i said",
        "that is not what i said",
        "useless questions",
        "too frustrating",
        "this is frustrating",
        "im over this",
        "i'm over this",
        "im done with this",
        "i'm done with this",
        "stop asking",
        "stop repeating",
        "already answered",
    ]

    return any(
        phrase in normalized
        for phrase in complaint_patterns
    )


def user_wants_to_stop(text):
    """Recognize explicit requests to stop the assessment."""

    normalized = normalize_text(text)

    stop_phrases = [
        "exit",
        "quit",
        "stop the assessment",
        "stop this assessment",
        "i want to stop",
        "i want to quit",
        "leave me alone",
        "end the assessment",
    ]

    return (
        normalized in stop_phrases
        or any(
            phrase in normalized
            for phrase in stop_phrases[2:]
        )
    )


def get_targeted_evidence(
    user_response,
    previous_objective,
):
    """
    Return evidence only for the attribute targeted by the
    previous question.

    Contextual extraction takes priority because it can interpret
    short answers using the previous objective.
    """

    if not previous_objective:
        # The opening message describes the user's concern.
        return extract_behavioral_evidence(user_response)

    construct = previous_objective.get("construct")
    attribute = previous_objective.get("attribute")

    if not construct or not attribute:
        return {}

    contextual_evidence = extract_contextual_answer(
        user_response,
        previous_objective,
    )

    general_evidence = extract_behavioral_evidence(
        user_response
    )

    contextual_attributes = contextual_evidence.get(
        construct, {}
    )

    general_attributes = general_evidence.get(
        construct, {}
    )

    # Use contextual evidence first.
    if attribute in contextual_attributes:
        value = contextual_attributes[attribute]

    # Otherwise, accept general evidence only if it matches
    # the current objective.
    elif attribute in general_attributes:
        value = general_attributes[attribute]

    else:
        return {}

    return {
        construct: {
            attribute: value,
        }
    }


def process_user_response(state, user_response):
    """
    Process one user response and generate the next question.

    Returns:
        The next objective dictionary, or None when the
        assessment should stop.
    """

    print("\n" + "=" * 60)
    print("USER RESPONSE")
    print("=" * 60)
    print(user_response)

    conversation = state["conversation"]

    # Save the answer once.
    add_user_response(state, user_response)

    history = conversation.setdefault("history", [])
    history.append({
        "role": "User",
        "text": user_response,
    })

    # Handle explicit stop requests.
    if user_wants_to_stop(user_response):
        print("\nAssessment ended at your request.")
        conversation["last_objective"] = None
        return None

    previous_objective = conversation.get("last_objective")
    current_turn = conversation["turn_count"]

    # Track unsuccessful answers separately for each objective.
    objective_attempts = conversation.setdefault(
        "objective_attempts", {}
    )

    extracted_evidence = get_targeted_evidence(
        user_response,
        previous_objective,
    )

    objective_key = None

    if previous_objective:
        construct = previous_objective["construct"]
        attribute = previous_objective["attribute"]

        objective_key = f"{construct}.{attribute}"

        has_valid_evidence = (
            construct in extracted_evidence
            and attribute in extracted_evidence[construct]
        )

        if has_valid_evidence:
            # Evidence was collected. Reset the attempt counter.
            objective_attempts[objective_key] = 0

        else:
            # No evidence was found for the current objective.
            attempts = objective_attempts.get(
                objective_key, 0
            ) + 1

            objective_attempts[objective_key] = attempts

            if is_conversation_complaint(user_response):
                print(
                    "\nI'm sorry. I may have misunderstood you "
                    "or repeated a question."
                )

                # Skip this objective rather than probing again.
                attempts = MAX_UNCLEAR_ATTEMPTS
                objective_attempts[objective_key] = attempts

                        
                if attempts >= MAX_UNCLEAR_ATTEMPTS:
                    # Record that this objective was skipped.
                    # Do not save "unanswered" as behavioral evidence.
                    skipped_objectives = conversation.setdefault(
                        "skipped_objectives", []
                    )

                    if objective_key not in skipped_objectives:
                        skipped_objectives.append(objective_key)

                    # Leave the actual attribute unknown.
                    extracted_evidence = {}

                    print(
                        f"\nThe objective '{attribute}' could not be "
                        f"established after {attempts} unsuccessful "
                        "attempts. Skipping it without recording "
                        "behavioral evidence."
                    )

            else:
                print(
                    "\nI couldn't identify a clear answer to "
                    "the current question. I'll try one "
                    "clarification."
                )

    print("\nEXTRACTED EVIDENCE:")
    print(extracted_evidence)

    # Update topic information and evidence only once.
    update_conversation_topic(
        state,
        extracted_evidence,
    )

    if extracted_evidence:
        apply_extracted_evidence(
            state=state,
            extracted_evidence=extracted_evidence,
            source_turn=current_turn,
        )
    else:
        print(
            "No evidence was recorded for this response."
        )

    print("\nUPDATED WORRY STATE:")
    print(state["constructs"]["worry"])

    # Ask the controller what evidence is needed next.
    objective = get_next_assessment_objective(state)

    print("\nNEXT ASSESSMENT OBJECTIVE:")
    print(objective)

    if objective is None:
        print("\nNo additional assessment objective remains.")
        conversation["last_objective"] = None
        return None

    # Retrieve knowledge for the selected objective.
    passages = retrieve_semantic_passages(
        objective["objective"],
        top_k=3,
    )

    print("\nRETRIEVED SOURCES:")

    for passage in passages:
        print("-", passage.get("source", "Unknown source"))

    if not passages:
        print(
            "\nNo relevant knowledge passages were retrieved. "
            "The assessment cannot generate a grounded question "
            "for this turn."
        )
        conversation["last_objective"] = None
        return None

    # Generate a question for the controller-selected objective.
    question = generate_follow_up_question(
        objective["objective"],
        passages,
        current_concern=(
            conversation.get("current_concern")
            or conversation.get("current_topic")
        ),
        latest_response=user_response,
        conversation_history=history,
    )

    print("\nGENERATED FOLLOW-UP QUESTION:")
    print(question)

    # Store the generated question and its objective together.
    history.append({
        "role": "Assistant",
        "text": question,
    })

    conversation["last_objective"] = objective

    return objective


def main():
    """Run an interactive adaptive assessment."""

    state = create_assessment_state()

    print("=" * 60)
    print("INTERACTIVE ADAPTIVE ASSESSMENT")
    print("Type 'exit' to end the conversation.")
    print("=" * 60)

    user_response = input(
        "\nPlease describe something you have been worrying about:\n> "
    ).strip()

    if not user_response:
        print("No response entered. Ending assessment.")
        return

    if user_wants_to_stop(user_response):
        print("Assessment ended.")
        return

    objective = process_user_response(
        state,
        user_response,
    )

    while objective is not None:
        user_response = input(
            "\nYour answer:\n> "
        ).strip()

        if not user_response:
            print(
                "Please enter an answer, or type 'exit' to stop."
            )
            continue

        objective = process_user_response(
            state,
            user_response,
        )

    print("\n" + "=" * 60)
    print("FINAL ASSESSMENT SUMMARY")
    print("=" * 60)

    print("\nWorry evidence:")
    print(state["constructs"]["worry"])

    print(
        "\nTotal turns:",
        state["conversation"]["turn_count"],
    )

    print(
        "Evidence records:",
        len(state["evidence_history"]),
    )


if __name__ == "__main__":
    main()
