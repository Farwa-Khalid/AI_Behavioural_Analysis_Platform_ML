
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
    update_evidence,
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

from rag.llm.llm_evidence_extractor import (
    extract_semantic_evidence,
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
    """Recognize direct and informal requests to stop the assessment."""

    normalized = normalize_text(text).strip()

    stop_patterns = [
        # Direct stop requests: stop, stoppp, stop it, stop talking
        r"^(?:(?:yes|yeah|yep|no|nope|okay|ok)\s+)*"
        r"(?:please\s+)?stop+p*\b",

         r"\b(?:can you|could you|would you)\s+"
         r"(?:(?:please|pls)\s+)?stop+p*\b",
        # Explicit requests to end or leave
        r"\b(?:i want|i would like|i'd like)\s+"
        r"(?:to\s+)?(?:stop|quit|end)\b",

        r"\b(?:i do not|i don't|i dont)\s+"
        r"want to continue\b",

        r"\b(?:leave me alone|end the assessment|"
        r"stop the assessment|stop this assessment)\b",

        # Standalone exit commands
        r"^(?:exit|quit|end)$",
    ]

    return any(
        re.search(pattern, normalized)
        for pattern in stop_patterns
    )


def get_targeted_evidence(
    user_response,
    previous_objective,
):
    """
    Preserve all clearly extracted behavioral evidence.

    Contextual extraction receives priority for the current
    assessment objective, while general extraction can capture
    additional evidence volunteered in the same response.
    """

    # The opening message describes the user's concern.
    if not previous_objective:
        return extract_behavioral_evidence(user_response)

    construct = previous_objective.get("construct")
    attribute = previous_objective.get("attribute")

    if not construct or not attribute:
        return {}

    # --------------------------------------------------------
    # 1. Extract evidence using the current question context
    # --------------------------------------------------------

    contextual_evidence = extract_contextual_answer(
        user_response,
        previous_objective,
    )
        # --------------------------------------------------------
    # Capture rumination frequency as secondary evidence
    # --------------------------------------------------------

    if (
        construct == "rumination"
        and attribute != "frequency"
    ):

        frequency_objective = {
            "construct": "rumination",
            "attribute": "frequency",
        }

        frequency_evidence = extract_contextual_answer(
            user_response,
            frequency_objective,
        )

        for evidence_construct, attributes in frequency_evidence.items():

            contextual_evidence.setdefault(
                evidence_construct,
                {},
            )

            contextual_evidence[evidence_construct].update(
                attributes
            )

    # --------------------------------------------------------
    # 2. Extract other evidence independently
    # --------------------------------------------------------

    general_evidence = extract_behavioral_evidence(
        user_response
    )

    # --------------------------------------------------------
    # 3. Preserve general evidence from all constructs
    # --------------------------------------------------------

    combined_evidence = {}

    for detected_construct, attributes in general_evidence.items():

        if not isinstance(attributes, dict):
            continue

        combined_evidence[detected_construct] = dict(attributes)

    # --------------------------------------------------------
    # 4. Merge contextual evidence
    # --------------------------------------------------------

    for contextual_construct, attributes in contextual_evidence.items():

        if not isinstance(attributes, dict):
            continue

        combined_evidence.setdefault(
            contextual_construct,
            {},
        )

        # Contextual evidence takes priority when the same
        # attribute was extracted by both methods.
        combined_evidence[contextual_construct].update(
            attributes
        )

    return combined_evidence

def get_semantic_evidence(
    user_response,
    conversation_history=None,
):
    """
    Extract additional behavioural evidence using Gemini.

    This function does not update assessment state.
    It returns the semantic extractor's result for later processing.
    """

    # Build context from previous conversation turns.
    previous_history = conversation_history or []

    # Exclude the current response because it is passed separately.
    if (
        previous_history
        and previous_history[-1].get("role") == "User"
        and previous_history[-1].get("text") == user_response
    ):
        previous_history = previous_history[:-1]

    context_lines = []

    for message in previous_history[-6:]:

        role = message.get("role", "Unknown")
        text = message.get("text", "")

        if text:
            context_lines.append(f"{role}: {text}")

    conversation_context = (
        "\n".join(context_lines)
        if context_lines
        else "No previous conversation."
    )

    try:

        result = extract_semantic_evidence(
            user_response=user_response,
            conversation_context=conversation_context,
        )

        return result

    except Exception as exc:

        print(
            "Semantic evidence extraction encountered an error:",
            exc,
        )

        return {
            "status": "unavailable",
            "original_response": user_response,
            "evidence": [],
            "clarification_question": None,
            "error": str(exc),
        }
        
def process_user_response(state, user_response):
    """
    Process one user response and generate the next question.

    Returns:
        - Objective dictionary when assessment continues.
        - Confirmation marker when waiting for user permission.
        - Initial clarification marker when the first response is unclear.
        - None when assessment stops or completes.
    """

    print("\n" + "=" * 60)
    print("USER RESPONSE")
    print("=" * 60)
    print(user_response)

    conversation = state["conversation"]

    # --------------------------------------------------------
    # 1. Save user response
    # --------------------------------------------------------

    add_user_response(state, user_response)

    history = conversation.setdefault("history", [])
    history.append({
        "role": "User",
        "text": user_response,
    })

    normalized_response = normalize_text(user_response)

    confirmed_continue = False

    # --------------------------------------------------------
    # 2. Handle pending continue/stop confirmation
    # --------------------------------------------------------

    if conversation.get("awaiting_continue_confirmation", False):

        continue_patterns = [
            r"^(?:yes|yeah|yep|sure|okay|ok)(?:\s|$)",
            r"^continue(?:\s|$)",
            r"^go on(?:\s|$)",
            r"^lets continue(?:\s|$)",
            r"^(?:no|nope)\s+i want to continue(?:\s|$)",
            r"^(?:no|nope)\s+i would like to continue(?:\s|$)",
            r"^i want to continue(?:\s|$)",
            r"^i would like to continue(?:\s|$)",
            r"^continue the assessment(?:\s|$)",
        ]

        stop_patterns = [
            r"^(?:no|nope)(?:\s|$)",
            r"^no thanks(?:\s|$)",
            r"^no thank you(?:\s|$)",
            r"^stop(?:\s|$)",
            r"^end(?:\s|$)",
            r"^stop the assessment(?:\s|$)",
            r"^i want to stop(?:\s|$)",
            r"^i do not want to continue(?:\s|$)",
            r"^i dont want to continue(?:\s|$)",
            r"^i would rather stop(?:\s|$)",
        ]

        wants_to_continue = any(
            re.search(pattern, normalized_response)
            for pattern in continue_patterns
        )

        wants_to_stop = any(
            re.search(pattern, normalized_response)
            for pattern in stop_patterns
        )

        if wants_to_continue:

            conversation["awaiting_continue_confirmation"] = False
            conversation["last_objective"] = None

            confirmed_continue = True

            print(
                "\nThank you. We can continue the assessment."
            )

        elif wants_to_stop or user_wants_to_stop(user_response):

            conversation["awaiting_continue_confirmation"] = False
            conversation["exit_requested"] = True
            conversation["termination_reason"] = "user_exit"
            conversation["last_objective"] = None

            print(
                "\nThank you for your time. "
                "Goodbye!"
            )

            return None

        else:

            print(
                "\nI just need a clear choice. "
                "Would you like to continue the assessment, "
                "or would you prefer to stop here?"
            )

            return {"status": "awaiting_confirmation"}

    # --------------------------------------------------------
    # 3. Handle explicit exit requests
    # --------------------------------------------------------

    if user_wants_to_stop(user_response):

        print("\nAssessment ended at your request.")

        conversation["last_objective"] = None
        conversation["exit_requested"] = True
        conversation["termination_reason"] = "user_exit"

        return None

    previous_objective = conversation.get("last_objective")
    current_turn = conversation["turn_count"]

    objective_attempts = conversation.setdefault(
        "objective_attempts", {}
    )

    # --------------------------------------------------------
    # 4. Detect complaints
    # --------------------------------------------------------

    complaint_detected = False

    if not confirmed_continue:

        complaint_detected = is_conversation_complaint(
            user_response
        )

    if complaint_detected:

        print(
            "\nI'm sorry. I may have misunderstood you "
            "or repeated a question."
        )

    # --------------------------------------------------------
    # 5. Detect explicit worry denial
    # --------------------------------------------------------

    worry_denial_patterns = [
        r"\b(?:i am not|im not|i'm not)\s+"
        r"(?:currently\s+)?worrying about anything\b",

        r"\b(?:i am not|im not|i'm not)\s+"
        r"(?:currently\s+)?worried about anything\b",

        r"\b(?:i am not|im not|i'm not)\s+"
        r"(?:currently\s+)?worried(?: right now)?\b",

        r"\bnot worrying about anything\b",

        r"\bi have nothing to worry about\b",

        r"\bno worries right now\b",
    ]

    explicit_worry_denial = (
        not confirmed_continue
        and any(
            re.search(pattern, normalized_response)
            for pattern in worry_denial_patterns
        )
    )

    current_construct = (
        previous_objective.get("construct")
        if previous_objective
        else None
    )

    # --------------------------------------------------------
    # 6. Extract evidence or handle special responses
    # --------------------------------------------------------

    # Default values for response paths that do not call Gemini.
    semantic_result = None
    semantic_known_evidence = {}
    semantic_uncertain_evidence = []
    rule_based_evidence = {}

    if confirmed_continue:

        # A confirmation response is not behavioural evidence.
        extracted_evidence = {}

    elif (
        explicit_worry_denial
        and current_construct in {None, "worry"}
    ):

        extracted_evidence = {
            "worry": {
                "detected": False,
            }
        }

        print(
            "\nExplicit worry denial recognized. "
            "The worry assessment will not continue."
        )

        if previous_objective:

            objective_key = (
                f"{previous_objective['construct']}."
                f"{previous_objective['attribute']}"
            )

            objective_attempts[objective_key] = 0

    elif complaint_detected:

        extracted_evidence = {}

        if previous_objective:

            construct = previous_objective["construct"]
            attribute = previous_objective["attribute"]

            objective_key = f"{construct}.{attribute}"

            objective_attempts[objective_key] = MAX_UNCLEAR_ATTEMPTS

            skipped_objectives = conversation.setdefault(
                "skipped_objectives", []
            )

            if objective_key not in skipped_objectives:
                skipped_objectives.append(objective_key)

            print(
                f"\nSkipping '{objective_key}' because "
                "the user expressed frustration."
            )

        conversation["last_objective"] = None
        conversation["awaiting_continue_confirmation"] = True

    else:

        # Normal rule-based evidence extraction.
        extracted_evidence = get_targeted_evidence(
            user_response,
            previous_objective,
        )
        
                # Preserve rule-based evidence separately.
        # Semantic evidence will be processed independently.
        rule_based_evidence = {
            construct: dict(attributes)
            for construct, attributes in extracted_evidence.items()
        }

        # Check whether the current objective was established.
        objective_evidence_found = False

        if previous_objective:

            construct = previous_objective["construct"]
            attribute = previous_objective["attribute"]

            objective_evidence_found = (
                construct in extracted_evidence
                and attribute in extracted_evidence[construct]
            )

        # Use semantic extraction when rule-based extraction
        # does not identify evidence for the current objective.
        semantic_result = None

        if (
            not extracted_evidence
            or (
                previous_objective
                and not objective_evidence_found
            )
        ):

            semantic_result = get_semantic_evidence(
                user_response,
                history,
            )

            print("\nSEMANTIC EXTRACTION STATUS:")
            print(semantic_result.get("status"))

            print("\nSEMANTIC EVIDENCE:")
            print(semantic_result.get("evidence", []))
            
        # Separate semantic evidence by confidence state.
        semantic_known_evidence = {}
        semantic_uncertain_evidence = []

        if (
            semantic_result
            and semantic_result.get("status") == "ok"
        ):

            for item in semantic_result.get("evidence", []):

                item_construct = item.get("construct")
                item_attribute = item.get("attribute")
                evidence_state = item.get("evidence_state")

                # Avoid duplicating evidence already found
                # by the rule-based extractor.
                if (
                    item_construct in extracted_evidence
                    and item_attribute
                    in extracted_evidence[item_construct]
                ):
                    continue

                if evidence_state == "known":

                    semantic_known_evidence.setdefault(
                        item_construct, {}
                    )[item_attribute] = item.get("value")

                elif evidence_state == "uncertain":

                    semantic_uncertain_evidence.append(item)


        # Apply the two-attempt rule to a current objective.
        if previous_objective:

            construct = previous_objective["construct"]
            attribute = previous_objective["attribute"]

            objective_key = f"{construct}.{attribute}"

            has_valid_evidence = (
                attribute in rule_based_evidence.get(
                    construct, {}
                )
                or attribute in semantic_known_evidence.get(
                    construct, {}
                )
            )

            has_uncertain_evidence = any(
                item.get("construct") == construct
                and item.get("attribute") == attribute
                for item in semantic_uncertain_evidence
            )

            if has_valid_evidence:

                objective_attempts[objective_key] = 0

            elif has_uncertain_evidence:

                # Do not count uncertain evidence as an
                # unsuccessful attempt. Clarification is needed.
                print(
                    "\nThe response contains potentially relevant "
                    "evidence that needs clarification."
                )

            else:

                attempts = objective_attempts.get(
                    objective_key, 0
                ) + 1

                objective_attempts[objective_key] = attempts

                if attempts >= MAX_UNCLEAR_ATTEMPTS:

                    skipped_objectives = conversation.setdefault(
                        "skipped_objectives", []
                    )

                    if objective_key not in skipped_objectives:
                        skipped_objectives.append(objective_key)


                    print(
                        f"\nThe objective '{attribute}' could "
                        f"not be established after {attempts} "
                        "unsuccessful attempts. Skipping it "
                        "without recording False."
                    )

                else:

                    print(
                        "\nI couldn't identify a clear answer "
                        "to the current question. I'll try "
                        "one clarification."
                    )

    # --------------------------------------------------------
    # 7. Update assessment state
    # --------------------------------------------------------

    print("\nEXTRACTED EVIDENCE:")
    print(extracted_evidence)

    # Update the conversation topic using rule-based evidence
    # and established semantic evidence.
    topic_evidence = {
        construct: dict(attributes)
        for construct, attributes in rule_based_evidence.items()
    }

    for construct, attributes in semantic_known_evidence.items():
        topic_evidence.setdefault(construct, {}).update(attributes)

    update_conversation_topic(
        state,
        topic_evidence,
    )

    # Store rule-based evidence using the existing method.
    if rule_based_evidence:

        apply_extracted_evidence(
            state=state,
            extracted_evidence=rule_based_evidence,
            source_turn=current_turn,
        )

    # Store semantic known evidence without inventing confidence.
    for construct, attributes in semantic_known_evidence.items():

        for attribute, value in attributes.items():

            update_evidence(
                state=state,
                construct=construct,
                attribute=attribute,
                value=value,
                evidence_state="known",
                source_turn=current_turn,
                confidence=None,
            )

    # Store semantic uncertain evidence in history only.
    for item in semantic_uncertain_evidence:

        update_evidence(
            state=state,
            construct=item["construct"],
            attribute=item["attribute"],
            value=item.get("value"),
            evidence_state="uncertain",
            source_turn=current_turn,
            confidence=None,
        )

    if not rule_based_evidence and not semantic_known_evidence:

        print(
            "No established evidence was recorded for this response."
        )
        
    print("\nUPDATED WORRY STATE:")
    print(state["constructs"]["worry"])
        # --------------------------------------------------------
    # End gracefully when the user explicitly denies worry
    # --------------------------------------------------------

    if explicit_worry_denial:

        print(
            "\nThank you for sharing. Since you have indicated "
            "that you are not worried, we can end this assessment here. "
            "Take care and goodbye!"
        )

        conversation["last_objective"] = None
        conversation["termination_reason"] = "explicit_worry_denial"
        conversation["awaiting_continue_confirmation"] = False

        return None
    # --------------------------------------------------------
    # Preserve the user's initial concern as conversation context
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Resume from the opening question after confirmation
    # --------------------------------------------------------

    if (
        confirmed_continue
        and previous_objective is None
        and not conversation.get("current_concern")
    ):

        opening_question = (
            "How have you been feeling or responding to situations "
            "in your everyday life recently? "
            "You can describe anything that has been on your mind "
            "or affected you."
        )

        print("\nLet's start again.")
        print(opening_question)

        history.append({
            "role": "Assistant",
            "text": opening_question,
        })

        conversation["initial_clarification_attempted"] = False

        return {
            "status": "awaiting_initial_concern"
        }

    # --------------------------------------------------------
    # Preserve the user's initial concern as conversation context
    # --------------------------------------------------------

    if (
        previous_objective is None
        and not conversation.get("current_concern")
        and not confirmed_continue
        and not complaint_detected
        and not explicit_worry_denial
        and user_response.strip()
    ):

        conversation["current_concern"] = user_response.strip()
    # --------------------------------------------------------
    # 8. Pause after a complaint
    # --------------------------------------------------------

    if conversation.get("awaiting_continue_confirmation", False):

        print(
            "\nWould you like to continue the assessment, "
            "or would you prefer to stop here?"
        )

        return {"status": "awaiting_confirmation"}
    
        # --------------------------------------------------------
    # 8A. Ask for clarification when semantic evidence is uncertain
    # --------------------------------------------------------

    semantic_clarification = (
        semantic_result.get("clarification_question")
        if semantic_result
        else None
    )

    if semantic_uncertain_evidence and semantic_clarification:

        print("\nSEMANTIC CLARIFICATION QUESTION:")
        print(semantic_clarification)

        history.append({
            "role": "Assistant",
            "text": semantic_clarification,
        })

        conversation["last_objective"] = previous_objective

        return {
            "status": "awaiting_semantic_clarification"
        }
        

    # --------------------------------------------------------
    # 9. Handle an unclear initial response
    # --------------------------------------------------------

    if (
        previous_objective is None
        and not rule_based_evidence
        and not semantic_known_evidence
        and not confirmed_continue
    ):

        clarification_attempted = conversation.get(
            "initial_clarification_attempted", False
        )

        if not clarification_attempted:

            conversation["initial_clarification_attempted"] = True

            current_concern = conversation.get("current_concern")

            if current_concern:

                clarification_question = (
                    f'You mentioned "{current_concern}". '
                    "Could you tell me a little more about "
                    "how you have been feeling or responding "
                    "in relation to that?"
                )

            else:

                clarification_question = (
                    "Could you tell me a little more about how "
                    "you have been feeling or responding to "
                    "different situations recently?"
                )

            print("\nCLARIFICATION QUESTION:")
            print(clarification_question)

            history.append({
                "role": "Assistant",
                "text": clarification_question,
            })

            return {
                "status": "awaiting_initial_clarification"
            }

        else:

            print(
                "\nI couldn't identify a clear behavioural "
                "pattern from your responses. That's okay. "
                "There is no need to force an answer."
            )

            conversation["last_objective"] = None
            conversation["termination_reason"] = (
                "no_construct_detected"
            )

            return None

    # --------------------------------------------------------
    # 10. Select next adaptive objective
    # --------------------------------------------------------

    objective = get_next_assessment_objective(state)

    print("\nNEXT ASSESSMENT OBJECTIVE:")
    print(objective)

    if objective is None:

        print(
            "\nNo additional assessment objective remains."
        )

        conversation["last_objective"] = None
        conversation["termination_reason"] = "completed"

        return None

    # --------------------------------------------------------
    # 11. Retrieve relevant RAG passages
    # --------------------------------------------------------

    passages = retrieve_semantic_passages(
        objective["objective"],
        top_k=3,
    )

    print("\nRETRIEVED SOURCES:")

    for passage in passages:
        print(
            "-",
            passage.get("source", "Unknown source")
        )

    if not passages:

        print(
            "\nNo relevant knowledge passages were retrieved. "
            "The assessment cannot generate a grounded question."
        )

        conversation["last_objective"] = None
        conversation["termination_reason"] = "retrieval_failure"

        return None

    # --------------------------------------------------------
    # 12. Generate follow-up question using Gemini
    # --------------------------------------------------------

    question = generate_follow_up_question(
        objective,
        passages,
        current_concern=(
            conversation.get("current_concern")
            or conversation.get("current_topic")
        ),
        latest_response=user_response,
        conversation_history=history,
    )

    # --------------------------------------------------------
    # Handle unavailable or repeated questions
    # --------------------------------------------------------

    if not question:

        print(
            "\nNo suitable new question could be generated "
            "for this assessment objective without repeating "
            "an earlier question."
        )

        conversation["last_objective"] = None
        conversation["termination_reason"] = (
            "no_non_repeated_question"
        )

        return None

    print("\nGENERATED FOLLOW-UP QUESTION:")
    print(question)

    history.append({
        "role": "Assistant",
        "text": question,
    })

    conversation["last_objective"] = objective

    return objective


def main():
    """Run an interactive adaptive assessment."""

    state = create_assessment_state()

    conversation = state["conversation"]

    # Initialize conversation-control variables.
    conversation["awaiting_continue_confirmation"] = False
    conversation["exit_requested"] = False
    conversation["termination_reason"] = None
    conversation["initial_clarification_attempted"] = False

    print("=" * 60)
    print("INTERACTIVE ADAPTIVE ASSESSMENT")
    print("Type 'exit' to end the conversation.")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Initial neutral question
    # --------------------------------------------------------

    user_response = input(
        "\nHow have you been feeling or responding to situations "
        "in your everyday life recently?\n"
        "You can describe anything that has been on your mind "
        "or affected you.\n> "
    ).strip()

    if not user_response:

        print("No response entered. Ending assessment.")

        conversation["termination_reason"] = "no_response"
        objective = None

    elif user_wants_to_stop(user_response):

        print("Assessment ended at your request.")

        conversation["exit_requested"] = True
        conversation["termination_reason"] = "user_exit"

        objective = None

    else:

        objective = process_user_response(
            state,
            user_response,
        )

    # --------------------------------------------------------
    # 2. Interactive conversation loop
    # --------------------------------------------------------

    while objective is not None:

        user_response = input(
            "\nYour answer:\n> "
        ).strip()

        if not user_response:

            print(
                "Please enter a response, or type 'exit' to stop."
            )

            continue

        objective = process_user_response(
            state,
            user_response,
        )

    # --------------------------------------------------------
    # 3. Final assessment summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL ASSESSMENT SUMMARY")
    print("=" * 60)

    termination_reason = conversation.get(
        "termination_reason"
    )

    if termination_reason == "completed":

        print("\nAssessment completed successfully.")

    elif termination_reason == "user_exit":

        print("\nAssessment stopped at your request.")

    elif termination_reason == "retrieval_failure":

        print(
            "\nAssessment stopped because relevant "
            "knowledge passages could not be retrieved."
        )

    elif termination_reason == "no_response":

        print(
            "\nAssessment ended because no response was provided."
        )

    elif termination_reason == "no_construct_detected":

        print(
            "\nNo clear behavioural pattern was identified "
            "during this assessment."
        )
    elif termination_reason == "no_non_repeated_question":

        print(
            "\nAssessment stopped because no suitable new "
            "question was available without repeating an "
            "earlier question."
        )

    # Display evidence for every construct.
    print("\nCOLLECTED BEHAVIOURAL EVIDENCE")
    print("-" * 60)

    for construct, attributes in state["constructs"].items():

        collected_attributes = {
            attribute: value
            for attribute, value in attributes.items()
            if value is not None
        }

        if collected_attributes:

            print(f"\n{construct.upper().replace('_', ' ')}:")

            for attribute, value in collected_attributes.items():

                print(f"  {attribute}: {value}")

    print(
        "\nTotal turns:",
        conversation["turn_count"],
    )

    print(
        "Evidence records:",
        len(state["evidence_history"]),
    )




if __name__ == "__main__":
    main()