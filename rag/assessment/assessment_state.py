"""
assessment_state.py

Maintains the current behavioral evidence collected during
the adaptive neuroticism assessment.

This file does NOT:
- generate questions
- retrieve RAG documents
- call an LLM
- make a diagnosis
- calculate a new neuroticism score

Its responsibility is to maintain the assessment state.
"""

from copy import deepcopy
from typing import Any, Dict, Optional


# ============================================================
# 1. VALID EVIDENCE STATES
# ============================================================

EVIDENCE_STATES = {
    "known",
    "unknown",
    "uncertain",
}


# ============================================================
# 2. BEHAVIORAL CONSTRUCTS AND THEIR ATTRIBUTES
# ============================================================

CONSTRUCTS = {

    "repetitive_negative_thinking": [
        "detected",
        "negative_content",
        "repetition",
        "persistence",
        "controllability",
        "switching_difficulty",
        "functional_impact",
        "context",
        "content",
    ],

    "worry": [
        "detected",
        "temporal_orientation",
        "negative_outcome",
        "content",
        "repetition",
        "frequency",
        "persistence",
        "controllability",
        "switching_difficulty",
        "perceived_likelihood",
        "perceived_severity",
        "perceived_coping",
        "functional_impact",
    ],

    "rumination": [
        "detected",
        "temporal_orientation",
        "content",
        "trigger",
        "repetition",
        "persistence",
        "controllability",
        "switching_difficulty",
        "self_focus",
        "post_event_thinking",
        "functional_impact",
    ],

    "emotional_reactivity": [
        "detected",
        "trigger",
        "sensitivity",
        "intensity",
        "persistence",
        "recovery",
        "controllability",
        "functional_impact",
        "repeated_pattern",
    ],

    "social_evaluation": [
        "detected",
        "context",
        "negative_expectation",
        "perceived_judgment",
        "criticism_sensitivity",
        "emotional_reactivity",
        "avoidance",
        "post_event_thinking",
        "persistence",
        "controllability",
    ],

    "stress_vulnerability": [
        "detected",
        "trigger",
        "perceived_stress",
        "feeling_overwhelmed",
        "perceived_coping",
        "coping_difficulty",
        "recovery",
        "persistence",
        "functional_impact",
        "repeated_pattern",
    ],

    "negative_self_evaluation": [
        "detected",
        "trigger",
        "self_doubt",
        "self_criticism",
        "perceived_failure",
        "perceived_inadequacy",
        "persistence",
        "controllability",
        "emotional_reactivity",
        "functional_impact",
    ],
}


# ============================================================
# 3. CREATE A NEW ASSESSMENT STATE
# ============================================================

def create_assessment_state() -> Dict[str, Any]:
    """
    Create a completely new assessment state.

    At the beginning, all behavioral evidence is None because
    we have not collected any information yet.
    """

    constructs = {}

    for construct, attributes in CONSTRUCTS.items():

        constructs[construct] = {
            attribute: None
            for attribute in attributes
        }

    return {
        "constructs": constructs,

       "conversation": {
        "turn_count": 0,
        "recent_responses": [],
        "current_topic": None,
        "current_concern": None,
    },

        "model_output": {
            "neurotic_probability": None,
            "non_neurotic_probability": None,
            "confidence": None,
        },

        "evidence_history": [],
    }


# ============================================================
# 4. VALIDATE CONSTRUCT
# ============================================================

def _validate_construct(construct: str) -> None:
    """
    Make sure the construct exists in our schema.
    """

    if construct not in CONSTRUCTS:

        raise ValueError(
            f"Unknown construct: '{construct}'. "
            f"Valid constructs: {list(CONSTRUCTS.keys())}"
        )


# ============================================================
# 5. VALIDATE ATTRIBUTE
# ============================================================

def _validate_attribute(
    construct: str,
    attribute: str,
) -> None:
    """
    Make sure the attribute belongs to the selected construct.
    """

    _validate_construct(construct)

    if attribute not in CONSTRUCTS[construct]:

        raise ValueError(
            f"Unknown attribute '{attribute}' "
            f"for construct '{construct}'. "
            f"Valid attributes: {CONSTRUCTS[construct]}"
        )


# ============================================================
# 6. UPDATE ONE PIECE OF EVIDENCE
# ============================================================

def update_evidence(
    state: Dict[str, Any],
    construct: str,
    attribute: str,
    value: Any,
    evidence_state: str = "known",
    source_turn: Optional[int] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Add or update one behavioral evidence attribute.
    """

    # Check that construct + attribute are valid.
    _validate_attribute(construct, attribute)

    # Check evidence state.
    if evidence_state not in EVIDENCE_STATES:

        raise ValueError(
            f"Invalid evidence state: '{evidence_state}'. "
            f"Use: {sorted(EVIDENCE_STATES)}"
        )

    # Check confidence if provided.
    if confidence is not None:

        if not 0 <= confidence <= 1:

            raise ValueError(
                "confidence must be between 0 and 1."
            )

    # Store the current value.
    state["constructs"][construct][attribute] = value

    # Also keep a history of where this evidence came from.
    evidence_record = {
        "construct": construct,
        "attribute": attribute,
        "value": value,
        "state": evidence_state,
        "source_turn": source_turn,
        "confidence": confidence,
    }

    state["evidence_history"].append(evidence_record)

    return state

def apply_extracted_evidence(
    state,
    extracted_evidence,
    source_turn=None,
    confidence=0.8
):
    """
    Add evidence produced by evidence_extractor.py
    into the assessment state.

    Parameters:
        state:
            The current assessment state.

        extracted_evidence:
            Dictionary returned by
            extract_behavioral_evidence().

        source_turn:
            Conversation turn that produced the evidence.

        confidence:
            Confidence assigned to the extracted evidence.

    Returns:
        Updated assessment state.
    """

    if not isinstance(extracted_evidence, dict):
        raise TypeError("extracted_evidence must be a dictionary")

    if source_turn is None:
        source_turn = state["conversation"]["turn_count"]

    for construct, attributes in extracted_evidence.items():

        if construct not in CONSTRUCTS:
            continue

        if not isinstance(attributes, dict):
            continue

        for attribute, value in attributes.items():

            if attribute not in CONSTRUCTS[construct]:
                continue

            update_evidence(
                state=state,
                construct=construct,
                attribute=attribute,
                value=value,
                evidence_state="known",
                source_turn=source_turn,
                confidence=confidence,
            )

    return state

# ============================================================
# 7. GET ONE PIECE OF EVIDENCE
# ============================================================

def get_evidence(
    state: Dict[str, Any],
    construct: str,
    attribute: str,
) -> Any:
    """
    Return the current value of one attribute.
    """

    _validate_attribute(construct, attribute)

    return state["constructs"][construct][attribute]


# ============================================================
# 8. FIND UNKNOWN ATTRIBUTES
# ============================================================

def get_unknown_attributes(
    state: Dict[str, Any],
    construct: Optional[str] = None,
) -> Dict[str, list]:
    """
    Find attributes that have not been collected yet.

    If construct is provided, only that construct is checked.
    """

    if construct is not None:

        _validate_construct(construct)

        constructs_to_check = [construct]

    else:

        constructs_to_check = list(CONSTRUCTS.keys())

    unknown = {}

    for current_construct in constructs_to_check:

        unknown[current_construct] = [

            attribute

            for attribute, value
            in state["constructs"][current_construct].items()

            if value is None
        ]

    return unknown


# ============================================================
# 9. FIND UNCERTAIN EVIDENCE
# ============================================================

def get_uncertain_attributes(
    state: Dict[str, Any],
) -> list:
    """
    Return evidence records that were marked uncertain.
    """

    return [

        record

        for record in state["evidence_history"]

        if record["state"] == "uncertain"
    ]


# ============================================================
# 10. ADD USER RESPONSE
# ============================================================

def add_user_response(
    state: Dict[str, Any],
    response: str,
) -> Dict[str, Any]:
    """
    Add a user response to conversation history.

    This function does NOT analyze the response.
    Evidence extraction will be handled separately.
    """

    if not isinstance(response, str):

        raise TypeError(
            "response must be a string."
        )

    response = response.strip()

    if not response:

        raise ValueError(
            "response cannot be empty."
        )

    # Increase turn number.
    state["conversation"]["turn_count"] += 1

    # Store the response.
    state["conversation"]["recent_responses"].append({

        "turn":
            state["conversation"]["turn_count"],

        "text":
            response,
    })

    return state


def update_conversation_topic(state, extracted_evidence):
    """
    Save the latest topic or concern identified by the extractor.

    The stored phrase comes from the user's own response.
    It is not a diagnosis or an inferred personality trait.
    """

    worry_evidence = extracted_evidence.get("worry", {})
    content = worry_evidence.get("content")

    if isinstance(content, str) and content.strip():
        state["conversation"]["current_topic"] = content.strip()

    return state

# ============================================================
# 11. UPDATE EXISTING ML MODEL OUTPUT
# ============================================================

def update_model_output(
    state: Dict[str, Any],
    neurotic_probability: Optional[float] = None,
    non_neurotic_probability: Optional[float] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Store the prediction produced by the existing
    neuroticism ML model.

    This function does NOT calculate the prediction.
    """

    values = {

        "neurotic_probability":
            neurotic_probability,

        "non_neurotic_probability":
            non_neurotic_probability,

        "confidence":
            confidence,
    }

    for name, value in values.items():

        if value is not None:

            if not 0 <= value <= 1:

                raise ValueError(
                    f"{name} must be between 0 and 1."
                )

    state["model_output"].update(values)

    return state


# ============================================================
# 12. COPY ASSESSMENT STATE
# ============================================================

def copy_assessment_state(
    state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create an independent copy of the assessment state.

    Useful later when testing controller decisions.
    """

    return deepcopy(state)


# ============================================================
# 13. BASIC TEST
# ============================================================

if __name__ == "__main__":

    # Create empty state.
    state = create_assessment_state()

    print("Assessment state created.")

    print(
        "Initial turn count:",
        state["conversation"]["turn_count"]
    )

    # Simulate first user response.
    add_user_response(
        state,
        "I keep worrying that I might fail my presentation."
    )

    # Add evidence extracted from that response.
    update_evidence(
        state=state,
        construct="worry",
        attribute="detected",
        value=True,
        evidence_state="known",
        source_turn=1,
        confidence=0.96,
    )

    update_evidence(
        state=state,
        construct="worry",
        attribute="temporal_orientation",
        value="future",
        evidence_state="known",
        source_turn=1,
        confidence=0.98,
    )

    update_evidence(
        state=state,
        construct="worry",
        attribute="negative_outcome",
        value="presentation failure",
        evidence_state="known",
        source_turn=1,
        confidence=0.94,
    )

    print()
    print("Current worry evidence:")
    print(state["constructs"]["worry"])

    print()
    print("Unknown worry attributes:")
    print(get_unknown_attributes(state, "worry"))

    print()
    print("Evidence history:")

    for item in state["evidence_history"]:

        print(item)