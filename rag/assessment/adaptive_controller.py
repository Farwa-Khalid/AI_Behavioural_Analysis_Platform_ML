"""
Adaptive Assessment Controller

Purpose:
    Examine the current behavioral assessment state and decide
    what evidence should be collected next.

Important:
    This controller does NOT generate the final question.
    It only decides WHAT information is missing.

Flow:

    Assessment State
          ↓
    Find missing evidence
          ↓
    Select highest-priority evidence
          ↓
    Return a question objective
"""


# ============================================================
# 1. Evidence priorities
# ============================================================

EVIDENCE_PRIORITIES = {
    "detected": 1,
    "temporal_orientation": 2,
    "trigger": 3,
    "content": 3,
    "frequency": 4,
    "intensity": 5,
    "persistence": 6,
    "controllability": 7,
    "switching_difficulty": 8,
    "functional_impact": 9,
    "recovery": 10,
    "repetition": 4,
}

CONSTRUCT_SPECIFICITY = {
    "social_evaluation": 1,
    "rumination": 1,
    "emotional_reactivity": 1,
    "stress_vulnerability": 1,
    "negative_self_evaluation": 1,

    "worry": 2,

    "repetitive_negative_thinking": 3,
}

# ============================================================
# 2. Construct-specific priorities
# ============================================================

CONSTRUCT_PRIORITY = {
    # Specific forms of repetitive negative thinking
    "worry": 1,
    "rumination": 1,

    # More specific behavioral domains
    "social_evaluation": 2,
    "emotional_reactivity": 2,
    "stress_vulnerability": 2,
    "negative_self_evaluation": 2,

    # Broad cross-cutting construct
    "repetitive_negative_thinking": 3,
}


# ============================================================
# 3. Find missing evidence
# ============================================================

def find_missing_evidence(state):
    """
    Find attributes that are still unknown.

    None means that we do not currently have evidence
    about that attribute.

    Returns:
        List of dictionaries describing missing evidence.
    """

    missing = []

    constructs = state.get("constructs", {})

    for construct, attributes in constructs.items():

        for attribute, value in attributes.items():

            if value is None:

                missing.append({
                    "construct": construct,
                    "attribute": attribute,
                    "priority": EVIDENCE_PRIORITIES.get(
                        attribute,
                        100
                    ),
                    "construct_priority": CONSTRUCT_PRIORITY.get(
                        construct,
                        100
                    ),
                })

    return missing


# ============================================================
# 4. Sort missing evidence
# ============================================================

def rank_missing_evidence(missing):
    """
    Rank missing evidence according to:

        1. Construct importance
        2. Attribute importance

    Lower numbers mean higher priority.
    """

    return sorted(
        missing,
        key=lambda item: (
            item["construct_priority"],
            item["priority"]
        )
    )


# ============================================================
# 5. Select next evidence objective
# ============================================================

def select_next_evidence(state):
    """
    Select the highest-priority missing behavioral attribute.

    Objectives already recorded in conversation["skipped_objectives"]
    are ignored without changing their actual evidence values.
    """

    constructs = state.get("constructs", {})
    conversation = state.get("conversation", {})

    skipped_objectives = set(
        conversation.get("skipped_objectives", [])
    )

    detected_constructs = []

    # 1. Find detected constructs.
    for construct, attributes in constructs.items():
        if attributes.get("detected") is True:
            detected_constructs.append(construct)

    # 2. Ignore broad RNT when a specific construct exists.
    specific_constructs = {
        "worry",
        "rumination",
        "emotional_reactivity",
        "social_evaluation",
        "stress_vulnerability",
        "negative_self_evaluation",
    }

    if any(
        construct in detected_constructs
        for construct in specific_constructs
    ):
        detected_constructs = [
            construct
            for construct in detected_constructs
            if construct != "repetitive_negative_thinking"
        ]

    # 3. Stop if nothing has been detected.
    if not detected_constructs:
        return None

    # 4. Rank constructs by specificity and priority.
    detected_constructs.sort(
        key=lambda construct: (
            CONSTRUCT_SPECIFICITY.get(construct, 100),
            CONSTRUCT_PRIORITY.get(construct, 100),
        )
    )

    # 5. Find missing attributes that have not been skipped.
    for construct in detected_constructs:
        attributes = constructs[construct]
        missing_attributes = []

        for attribute, value in attributes.items():

            if attribute == "detected":
                continue

            objective_key = f"{construct}.{attribute}"

            # Skip objectives the conversation has already skipped.
            if objective_key in skipped_objectives:
                continue

            # None means that evidence has not been established.
            if value is None:
                missing_attributes.append({
                    "construct": construct,
                    "attribute": attribute,
                    "priority": EVIDENCE_PRIORITIES.get(
                        attribute, 100
                    ),
                    "construct_priority": CONSTRUCT_PRIORITY.get(
                        construct, 100
                    ),
                })

        # 6. Select the highest-priority remaining attribute.
        if missing_attributes:
            ranked = rank_missing_evidence(
                missing_attributes
            )
            return ranked[0]

    # No eligible missing objectives remain.
    return None


    # --------------------------------------------------------
    # 7. No missing evidence
    # --------------------------------------------------------

    return None
# ============================================================
# 6. Human-readable objective
# ============================================================

def describe_evidence_objective(objective):
    """
    Convert an evidence objective into a human-readable
    description.

    This is NOT the final chatbot question.
    """

    if objective is None:
        return "No additional evidence is currently required."

    construct = objective["construct"]
    attribute = objective["attribute"]

    descriptions = {

        ("worry", "temporal_orientation"):
            "Determine whether the worry is mainly about the past, present, or future.",

        ("worry", "trigger"):
            "Identify what typically triggers the worry.",

        ("worry", "frequency"):
            "Determine how often the worry occurs.",

        ("worry", "intensity"):
            "Determine how intense the worry feels.",

        ("worry", "persistence"):
            "Determine how long the worry tends to continue.",

        ("worry", "controllability"):
            "Determine how easy or difficult it is to control the worry.",

        ("worry", "functional_impact"):
            "Determine whether the worry interferes with daily functioning.",
            
        ("worry", "switching_difficulty"):
    "Determine how easily the person can shift attention away from the worry.",

        ("worry", "perceived_likelihood"):
            "Explore how likely the person believes the feared outcome is.",

        ("worry", "perceived_severity"):
            "Explore how serious the person believes the feared outcome would be.",

        ("worry", "perceived_coping"):
            "Explore how capable the person feels of handling the feared outcome.",

        ("worry", "negative_outcome"):
            "Identify the negative outcome the person is concerned might happen.",

        ("worry", "content"):
            "Clarify what the person is worrying about.",

        ("worry", "repetition"):
            "Determine whether the same worry or thought keeps returning.",

        ("rumination", "trigger"):
            "Identify what event or situation usually starts the rumination.",

        ("rumination", "persistence"):
            "Determine how long the repeated thinking continues.",

        ("rumination", "controllability"):
            "Determine how difficult it is to stop the repeated thinking.",

        ("emotional_reactivity", "trigger"):
            "Identify situations that produce strong emotional reactions.",

        ("emotional_reactivity", "intensity"):
            "Determine how strongly the person reacts emotionally.",

        ("emotional_reactivity", "recovery"):
            "Determine how quickly the person returns to their normal emotional state.",

        ("social_evaluation", "negative_expectation"):
            "Determine whether the person expects negative judgment from others.",

        ("social_evaluation", "criticism_sensitivity"):
            "Determine how strongly criticism affects the person.",

        ("social_evaluation", "avoidance"):
            "Determine whether fear of judgment causes avoidance.",

        ("stress_vulnerability", "perceived_stress"):
            "Determine how strongly stressful situations are experienced.",

        ("stress_vulnerability", "perceived_coping"):
            "Determine how capable the person feels of coping with stress.",

        ("stress_vulnerability", "recovery"):
            "Determine how quickly the person recovers after stressful situations.",

        ("negative_self_evaluation", "self_doubt"):
            "Determine whether the person doubts their own abilities.",

        ("negative_self_evaluation", "self_criticism"):
            "Determine how strongly the person criticizes themselves.",

        ("negative_self_evaluation", "perceived_inadequacy"):
            "Determine whether the person frequently feels inadequate.",
    }

    return descriptions.get(
        (construct, attribute),
        f"Collect information about {attribute} for {construct}."
    )


# ============================================================
# 7. Main controller function
# ============================================================


def get_next_assessment_objective(state):
    """
    Return the next eligible assessment objective,
    or None if no objective remains.
    """

    objective = select_next_evidence(state)

    if objective is None:
        return None

    return {
        "construct": objective["construct"],
        "attribute": objective["attribute"],
        "priority": objective["priority"],
        "objective": describe_evidence_objective(objective),
    }

# ============================================================
# 8. Test
# ============================================================

if __name__ == "__main__":

    from rag.assessment.assessment_state import create_assessment_state
    
    state = create_assessment_state()

    print("=" * 60)
    print("INITIAL ASSESSMENT")
    print("=" * 60)

    next_objective = get_next_assessment_objective(state)

    print("\nNEXT OBJECTIVE:")
    print(next_objective)