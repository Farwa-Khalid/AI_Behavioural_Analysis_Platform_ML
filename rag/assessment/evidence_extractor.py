"""
Behavioral Evidence Extractor

Purpose:
    Convert a user's natural-language response into structured
    behavioral evidence that can be stored in assessment_state.py.

This is the first version of the extractor.
It intentionally uses transparent rules instead of an LLM.
"""

import re


def is_explicit_worry_denial(text):
    """Detect clear statements that the person does not experience worry."""

    text = text.lower().strip()

    denial_patterns = [
        r"\bi don't worry\b",
        r"\bi do not worry\b",
        r"\bi never worry\b",
        r"\bi rarely worry\b",
        r"\bi can't worry about anything\b",
        r"\bi cannot worry about anything\b",
        r"\bi am not worried\b",
        r"\bi'm not worried\b",
        r"\bi don't experience worry\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in denial_patterns
    )


# ============================================================
# 1. Keyword patterns
# ============================================================

WORRY_PATTERNS = [
    r"\bworry\b",
    r"\bworrying\b",
    r"\bworried\b",
    r"\bconcerned\b",
    r"\bafraid\b",
    r"\bfear\b",
    r"\bfearing\b",
    r"\bscared\b",
    r"\bwhat if\b",
]

RUMINATION_PATTERNS = [
    r"\bkeep thinking about\b",
    r"\bkeeps thinking about\b",
    r"\bcan't stop thinking about\b",
    r"\bcannot stop thinking about\b",
    r"\bthink about it over and over\b",
    r"\breplay\b",
    r"\breplaying\b",
    r"\bthinking about what happened\b",
    r"\bgo over it again\b",
]

EMOTIONAL_REACTIVITY_PATTERNS = [
    r"\boverwhelmed\b",
    r"\bvery emotional\b",
    r"\breact strongly\b",
    r"\breact badly\b",
    r"\bget upset easily\b",
    r"\bgets upset easily\b",
    r"\bvery upset\b",
    r"\bstrong reaction\b",

    # Informal expressions of emotional reactivity
    r"\bvery reactive\b",
    r"\bhighly reactive\b",
    r"\bemotionally reactive\b",
    r"\breactive person\b",
    r"\bi am reactive\b",
    r"\bi'm reactive\b",
    r"\bi feel reactive\b",
    r"\bi react emotionally\b",
    r"\bi overreact\b",
    r"\bi tend to overreact\b",
    r"\boverreact easily\b",
    r"\bvery sensitive to criticism\b",
]

SOCIAL_EVALUATION_PATTERNS = [
    r"\bwhat people think\b",
    r"\bwhat others think\b",
    r"\bjudg(e|ed|ing|ment)\b",
    r"\bcriticiz(e|ed|ing)\b",
    r"\bcriticism\b",
    r"\bembarrass(ed|ing|ment)?\b",
    r"\blook stupid\b",
    r"\bthink badly of me\b",
    r"\bwhat .* think of me\b",
    r"\bwhat .* think about me\b",
    r"\bpeople .* think of me\b",
    r"\bothers .* think of me\b",
]


STRESS_PATTERNS = [
    r"\bstressed\b",
    r"\bstress(?:ful)?\b",
    r"\boverwhelmed\b",
    r"\btoo much to handle\b",
    r"\bcan't handle\b",
    r"\bcannot handle\b",
    r"\bhard to cope\b",
    r"\bstruggle to cope\b",
    r"\bstruggling to cope\b",
    r"\bunable to cope\b",
    r"\bcan't cope\b",
    r"\bcannot cope\b",
]


SELF_EVALUATION_PATTERNS = [
    r"\bnot good enough\b",
    r"\bnot capable\b",
    r"\bI am a failure\b",
    r"\bI'm a failure\b",
    r"\bI failed\b",
    r"\bI blame myself\b",
    r"\bblame myself\b",
    r"\bself-doubt\b",
    r"\bdoubt myself\b",
    r"\bworthless\b",
]


# ============================================================
# 2. Helper function
# ============================================================

def _matches_any(text, patterns):
    """
    Check whether the text matches at least one pattern.

    Returns:
        True  -> a matching pattern was found
        False -> no matching pattern was found
    """

    text = text.lower()

    for pattern in patterns:
        if re.search(pattern, text):
            return True

    return False


# ============================================================
# 3. Detect repetition
# ============================================================

def detect_repetition(text):
    """
    Detect language suggesting repeated or persistent thinking.

    Example:
        "I keep worrying about failing."

    Returns:
        True or False
    """

    repetition_patterns = [
        r"\bkeep\b",
        r"\bkeeps\b",
        r"\bconstantly\b",
        r"\balways\b",
        r"\bover and over\b",
        r"\bagain and again\b",
        r"\bcan't stop\b",
        r"\bcannot stop\b",
        r"\ball the time\b",
        r"\boften\b",
        r"\brepeatedly\b",
    ]

    return _matches_any(text, repetition_patterns)


# ============================================================
# 4. Detect temporal orientation
# ============================================================

def detect_temporal_orientation(text):
    """
    Determine whether the response is mainly about the past,
    present, or future.

    Returns:
        "past"
        "present"
        "future"
        None
    """

    text = text.lower()

    future_patterns = [
        r"\bwill\b",
        r"\bgoing to\b",
        r"\bmight\b",
        r"\bmay\b",
        r"\bcould\b",
        r"\bwhat if\b",
        r"\bfuture\b",
        r"\btomorrow\b",
        r"\bnext week\b",
        r"\bnext month\b",
        r"\bnext year\b",
        r"\bi'll\b",
        r"\bi will\b",
        r"\bi might\b",
        r"\bi may\b",
        r"\bi could\b",
        r"\bfuture\b",
        r"\blater on\b",
        r"\bin the future\b",
        r"\bdown the road\b",
        r"\bupcoming\b",
        r"\bthings that might happen\b",
        r"\bpossibilities\b",
    ]

    past_patterns = [
    r"\byesterday\b",
    r"\blast night\b",
    r"\blast week\b",
    r"\blast month\b",
    r"\blast year\b",
    r"\bbefore\b",
    r"\bafter\b",
    r"\bhappened\b",
    r"\breplayed\b",
    r"\breplay\b",
    r"\bremember\b",
    r"\bremembering\b",
]

    present_patterns = [
        r"\bright now\b",
        r"\bcurrently\b",
        r"\btoday\b",
        r"\bthese days\b",
        r"\bat the moment\b",
        r"\bnow\b",
        r"\bpresent(?:ly)?\b",
        r"\bcurrent(?:ly)?\b",
        r"\bcurrent tasks?\b",
        r"\bcurrent work\b",
        r"\bcurrent situation\b",
        r"\bwhat i'm dealing with\b",
        r"\bwhat i am dealing with\b",
        r"\bthe work i'm doing\b",
        r"\bthe work i am doing\b",
    ]

    if _matches_any(text, future_patterns):
        return "future"

    if _matches_any(text, past_patterns):
        return "past"

    if _matches_any(text, present_patterns):
        return "present"

    return None


def extract_worry_content(text):
    """
    Extract the topic or negative outcome associated with worry
    or concern.
    """

    patterns = [
        r"\b(?:worry|worrying|worried|concerned|concern)\s+(?:that|about|whether|if)\s+(.+)",
        r"\bwhat if\s+(.+)",
        r"\b(?:afraid|fear|fearing)\s+(?:that|of)\s+(.+)",
    ]

    text = text.strip()

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            content = match.group(1).strip()
            content = content.rstrip(".,!?")

            if content:
                return content

    return None


def extract_persistence(text):
    """
    Extract how long a thought or worry continues.

    Returns a broad duration category:
        "minutes"
        "hours"
        "days"
        "brief"
        "uncertain"
        "variable"
        None
    """

    if not isinstance(text, str) or not text.strip():
        return None

    text_lower = text.lower().strip()

    # --------------------------------------------------------
    # 1. Check uncertainty first.
    # --------------------------------------------------------

    uncertain_patterns = [
        r"\bi don't know\b",
        r"\bi dont know\b",
        r"\bcan't specify\b",
        r"\bcannot specify\b",
        r"\bcan't tell\b",
        r"\bcannot tell\b",
        r"\bnot sure\b",
        r"\bhard to say\b",
        r"\bcan't say\b",
        r"\bcannot say\b",
        r"\bno idea\b",
    ]

    if any(
        re.search(pattern, text_lower)
        for pattern in uncertain_patterns
    ):
        return "uncertain"

    # --------------------------------------------------------
    # 2. Check variable duration.
    # --------------------------------------------------------

    variable_patterns = [
        r"\bit varies\b",
        r"\bvaries\b",
        r"\bdepends\b",
        r"\bsometimes .* other times\b",
        r"\bnot always the same\b",
        r"\bdifferent each time\b",
    ]

    if any(
        re.search(pattern, text_lower)
        for pattern in variable_patterns
    ):
        return "variable"

    # --------------------------------------------------------
    # 3. Check longer durations first.
    # --------------------------------------------------------

    duration_patterns = [

        ("days", [
            r"\bfor a couple of days\b",
            r"\bfor several days\b",
            r"\bfor days\b",
            r"\b2 days\b",
            r"\btwo days\b",
            r"\bthree days\b",
            r"\b3 days\b",
            r"\ball week\b",
            r"\bfor weeks\b",
            r"\b\d+\s*(?:days?|d)\b",
            r"\bafter a few days\b",
            r"\bafter several days\b",
            r"\bafter two days\b",
            r"\bafter three days\b",
            r"\ba few days\b",
            r"\bseveral days\b",
            r"\b\d+\s*(?:days?|d)\b",
        ]),

        ("hours", [
            # Numeric expressions:
            # 2 hours, 2 hrs, 1 hr, 3h
            r"\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|hr|h)\b",

            # Written number expressions:
            r"\bone hour\b",
            r"\btwo hours\b",
            r"\bthree hours\b",
            r"\bfour hours\b",
            r"\bfive hours\b",
            r"\bsix hours\b",
            r"\ba couple of hours\b",
            r"\bseveral hours\b",
            r"\bfor hours\b",
            r"\bfor an hour\b",
            r"\ban hour\b",
            r"\bhalf an hour\b",
            r"\bwhole hour\b",
            r"\bentire hour\b",
            r"\bwhole day\b",
            r"\bentire day\b",
            r"\ball day\b",
           r"\ban entire hr\b",
            r"\bentire hr\b",
        ]),

        ("minutes", [
            # Numeric expressions:
            # 30 minutes, 15 mins, 5 min
            r"\b\d+\s*(?:minutes?|mins?|min)\b",

            r"\bfor minutes\b",
            r"\bfor a few minutes\b",
            r"\bfor several minutes\b",
            r"\ba few minutes\b",
            r"\bseveral minutes\b",
            r"\bfor a short time\b",
            r"\bhalf an hour\b",
        ]),

        ("brief", [
            r"\bfor a second\b",
            r"\bfor seconds\b",
            r"\bfor a moment\b",
            r"\bfor a little while\b",
            r"\bfor some time\b",
            r"\bfor sometime\b",
            r"\bfor a while\b",
            r"\bfor some minutes\b",
            r"\bafter a while\b",
            r"\bafter some time\b",
            r"\bafter sometime\b",
            r"\ba while\b",
            r"\bsome time\b",
        ]),
    ]

    for duration, patterns in duration_patterns:

        if any(
            re.search(pattern, text_lower)
            for pattern in patterns
        ):
            return duration

    return None


def extract_controllability(text):
    """Extract whether the person can control or stop the thought."""

    text_lower = text.lower()

    difficult_patterns = [
        "hard to stop",
        "difficult to stop",
        "can't stop",
        "cannot stop",
        "unable to stop",
        "find it hard to stop",
        "find it difficult to stop",
        "can't control",
        "cannot control",
    ]

    manageable_patterns = [
        "can stop thinking",
        "can control my thoughts",
        "easy to stop",
        "able to stop",
    ]

    if any(phrase in text_lower for phrase in difficult_patterns):
        return "difficult"

    if any(phrase in text_lower for phrase in manageable_patterns):
        return "manageable"

    return None


def extract_frequency(text):
    """Extract how frequently the worry or situation occurs."""

    text_lower = text.lower()

    frequency_patterns = {
        "almost every time": [
            "almost every",
            "nearly every",
        ],
        "often": [
            "often",
            "frequently",
            "many times",
        ],
        "sometimes": [
            "sometimes",
            "occasionally",
        ],
        "rarely": [
            "rarely",
            "hardly ever",
            "seldom",
        ],
        "always": [
            "always",
            "every time",
            "each time",
        ],
    }

    for frequency, phrases in frequency_patterns.items():
        if any(phrase in text_lower for phrase in phrases):
            return frequency

    return None
# ============================================================
# 5. Extract worry evidence
# ============================================================

def extract_worry_evidence(text):
    """
    Extract worry evidence, including useful details from
    short answers to follow-up questions.
    """

    evidence = {}

    if _matches_any(text, WORRY_PATTERNS):
        evidence["detected"] = True

    temporal_orientation = detect_temporal_orientation(text)
    if temporal_orientation:
        evidence["temporal_orientation"] = temporal_orientation

    content = extract_worry_content(text)
    if content:
        evidence["content"] = content

    if detect_repetition(text):
        evidence["repetition"] = True

    persistence = extract_persistence(text)
    if persistence:
        evidence["persistence"] = persistence

    controllability = extract_controllability(text)
    if controllability:
        evidence["controllability"] = controllability

    frequency = extract_frequency(text)
    if frequency:
        evidence["frequency"] = frequency

    return evidence


# ============================================================
# 6. Extract rumination evidence
# ============================================================
def extract_rumination_evidence(text):
    """
    Extract evidence related to rumination.

    Rumination is treated as repeated thinking about
    past or current negative experiences.
    """

    evidence = {}

    if _matches_any(text, RUMINATION_PATTERNS):

        evidence["detected"] = True

        temporal_orientation = detect_temporal_orientation(text)

        if temporal_orientation:
            evidence["temporal_orientation"] = (
                temporal_orientation
            )

        # ------------------------------------------------
        # Capture the situation or event being replayed.
        # ------------------------------------------------

        content_patterns = [
            r"after (.+?) happens",
            r"about (.+)",
            r"replay (.+?) over and over",
            r"keep thinking about (.+)",
        ]

        for pattern in content_patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:

                content = match.group(1).strip()
                content = content.rstrip(".,!?")

                if content:
                    evidence["content"] = content

                break

        if detect_repetition(text):
            evidence["repetition"] = True

    return evidence

# ============================================================
# 7. Extract emotional reactivity evidence
# ============================================================

def extract_emotional_reactivity_evidence(text):
    """
    Detect language suggesting strong or difficult-to-control
    emotional reactions.
    """

    evidence = {}

    if _matches_any(text, EMOTIONAL_REACTIVITY_PATTERNS):
        evidence["detected"] = True

    return evidence


# ============================================================
# 8. Extract social evaluation evidence
# ============================================================

def extract_social_evaluation_evidence(text):
    """
    Detect concerns related to judgment, criticism, embarrassment,
    or other people's opinions.
    """

    evidence = {}

    if _matches_any(text, SOCIAL_EVALUATION_PATTERNS):
        evidence["detected"] = True

    return evidence


# ============================================================
# 9. Extract stress vulnerability evidence
# ============================================================


def extract_stress_vulnerability_evidence(text):
    """
    Detect explicit language suggesting stress, feeling
    overwhelmed, or difficulty coping.

    A generic statement about worrying is not sufficient
    evidence of stress vulnerability.
    """

    evidence = {}

    if not isinstance(text, str) or not text.strip():
        return evidence

    if _matches_any(text, STRESS_PATTERNS):
        evidence["detected"] = True

        text_lower = text.lower()

        if (
            "overwhelmed" in text_lower
            or "too much to handle" in text_lower
        ):
            evidence["feeling_overwhelmed"] = True

        if (
            "hard to cope" in text_lower
            or "struggle to cope" in text_lower
            or "struggling to cope" in text_lower
            or "unable to cope" in text_lower
            or "can't cope" in text_lower
            or "cannot cope" in text_lower
            or "can't handle" in text_lower
            or "cannot handle" in text_lower
        ):
            evidence["coping_difficulty"] = True

    return evidence


# ============================================================
# 10. Extract negative self-evaluation evidence
# ============================================================

def extract_negative_self_evaluation_evidence(text):
    """
    Detect negative judgments about one's own ability,
    worth, performance, or adequacy.
    """

    evidence = {}

    if _matches_any(text, SELF_EVALUATION_PATTERNS):
        evidence["detected"] = True

    return evidence


def extract_contextual_answer(text, objective):
    """
    Interpret a user's answer in the context of the current
    assessment objective.

    Returns evidence only for the attribute being assessed.
    This function does not diagnose the user.
    """

    if not isinstance(text, str) or not text.strip():
        return {}

    if not isinstance(objective, dict):
        return {}

    construct = objective.get("construct")
    attribute = objective.get("attribute")

    if construct not in {
        "worry",
        "rumination",
        "repetitive_negative_thinking",
        "stress_vulnerability",
        "emotional_reactivity",
        "social_evaluation",
        "negative_self_evaluation",
    }:
        return {}

    # Normalize punctuation, capitalization, and whitespace.
    answer = text.lower().replace("’", "'").strip()
    answer = re.sub(r"[.!?,;]+", " ", answer)
    answer = re.sub(r"\s+", " ", answer).strip()

    evidence = {}

    # --------------------------------------------------------
    # 1. Repetition: Does the same thought return?
    # --------------------------------------------------------
    if attribute == "repetition":

        positive_patterns = [
            r"\byes\b",
            r"\bexactly\b",
            r"\bthat's right\b",
            r"\bthats right\b",
            r"\bkeeps coming back\b",
            r"\bcomes back\b",
            r"\bcome back\b",
            r"\bstuck in my mind\b",
            r"\bover and over\b",
            r"\bagain and again\b",
            r"\bsame thought\b",
            r"\bsame memory\b",
            r"\bkeeps returning\b",
            r"\bsometimes\b",
            r"\boccasionally\b",
            r"\bfrom time to time\b",
            r"\bnow and then\b",
        ]

        negative_patterns = [
            r"\bno\b",
            r"\bzero times\b",
            r"\bnot at all\b",
            r"\bnever\b",
            r"\bdoesn't come back\b",
            r"\bdoes not come back\b",
            r"\bstays away\b",
            r"\bleaves my mind entirely\b",
            r"\bi moved on\b",
            r"\bit is gone\b",
            r"\bit's gone\b",
            r"\bit's not recurring\b",
            r"\bim chill\b",
            r"\bi'm chill\b",
            r"\bi am chill\b",
            r"\bnot worried\b",
        ]

        # Only interpret a clear yes/no or recurring-thought answer.
        if any(
            re.search(pattern, answer)
            for pattern in negative_patterns
        ):
            evidence["repetition"] = False

        elif any(
            re.search(pattern, answer)
            for pattern in positive_patterns
        ):
            evidence["repetition"] = True

    # --------------------------------------------------------
    # 2. Frequency: How often does the worry occur?
    # --------------------------------------------------------
    elif attribute == "frequency":

        # Check uncertainty first.
        uncertain_patterns = [
            r"\bi don't know\b",
            r"\bi dont know\b",
            r"\bnot sure\b",
            r"\bcan't say\b",
            r"\bcannot say\b",
            r"\bhard to say\b",
            r"\bno idea\b",
            r"\bi can't tell\b",
            r"\bi cannot tell\b",
        ]

        # Explicitly infrequent answers must be checked
        # before broad patterns such as "every time".
        rare_patterns = [
            r"\bnot too much\b",
            r"\bnot much\b",
            r"\bnot that much\b",
            r"\bnot very often\b",
            r"\bnot often\b",
            r"\bhardly ever\b",
            r"\brarely\b",
            r"\bseldom\b",
            r"\bonce a week\b",
            r"\bonly occasionally\b",
            r"\bonly sometimes\b",
        ]

        never_patterns = [
            r"\bzero times\b",
            r"\bno times\b",
            r"\bnever\b",
            r"\bnot at all\b",
            r"\bnot once\b",
        ]

        occasional_patterns = [
            r"\bsometimes\b",
            r"\bonce in a while\b",
            r"\boccasionally\b",
            r"\bnow and then\b",
            r"\bfrom time to time\b",
            r"\ba few days\b",
            r"\bcertain nights\b",
            r"\bsome nights\b",
            r"\b2\s*-\s*3 days\b",
            r"\b2 to 3 days\b",
            r"\ba couple of times\b",
            r"\btwo or three times\b",
            r"\b2 or 3 times\b",
            r"\b2 to 3 times\b",
            r"\btwice or thrice\b",
            r"\ba few times\b",
            r"\btwice a week\b",
            r"\btwo times a week\b",
            r"\b2 times a week\b",
            r"\bthrice a week\b",
            r"\bthree times a week\b",
            r"\b3 times a week\b",
        ]

        frequent_patterns = [
            r"\beverytime\b",
            r"\bevery time\b",
            r"\ball the time\b",
            r"\balmost all the time\b",
            r"\bconstantly\b",
            r"\bcontinually\b",
            r"\bevery single time\b",
            r"\bmost of the time\b",
            r"\balmost every day\b",
            r"\bevery day\b",
            r"\beveryday\b",
            r"\bdaily\b",
            r"\bvery often\b",
            r"\bfrequently\b",
            r"\bmany times\b",
            r"\ba lot\b",
            r"\bmost days\b",
            r"\btwice a day\b",
            r"\btwo times a day\b",
            r"\b2 times a day\b",
            r"\bthrice a day\b",
            r"\bthree times a day\b",
            r"\b3 times a day\b",
        ]

        if any(
            re.search(pattern, answer)
            for pattern in uncertain_patterns
        ):
            evidence["frequency"] = "uncertain"

        elif any(
            re.search(pattern, answer)
            for pattern in never_patterns
        ):
            evidence["frequency"] = "never"

        elif any(
            re.search(pattern, answer)
            for pattern in rare_patterns
        ):
            evidence["frequency"] = "rarely"

        elif any(
            re.search(pattern, answer)
            for pattern in occasional_patterns
        ):
            evidence["frequency"] = "sometimes"

        elif any(
            re.search(pattern, answer)
            for pattern in frequent_patterns
        ):
            evidence["frequency"] = "often"

  
    # --------------------------------------------------------
    # 3. Controllability and switching difficulty
    # --------------------------------------------------------
    elif attribute in {
        "controllability",
        "switching_difficulty",
    }:

        difficult_patterns = [
            "hard to stop",
            "difficult to stop",
            "can't stop",
            "cannot stop",
            "unable to stop",
            "hard to control",
            "difficult to control",
            "can't control",
            "cannot control",
            "stuck in my mind",
            "can't move on",
            "cannot move on",
            "hard to think about anything else",
            "still there in the back of my mind",
            "always in the back of my mind",
            "can't get it out of my mind",
            "cannot get it out of my mind",
            "keeps coming back",
            "takes effort to stop",
            "hard to switch off",
            "unable to switch it off",
            "struggle to manage",
            "find it difficult to manage",
            "cannot manage it",
            "can't manage it",
                        "struggle to control",
            "struggle with controlling",
            "find it hard to control",
            "difficulty controlling",
            "hard to manage",
            "difficult to manage",
        ]

        manageable_patterns = [
            "not that much difficult",
            "not very difficult",
            "not too difficult",
            "not difficult",
            "easy to stop",
            "can stop",
            "able to stop",
            "can control it",
            "easy to control",
            "i moved on",
            "leaves my mind",
            "im chill",
            "i'm chill",
            "i am chill",
            "can shift my attention",
            "can focus on something else",
            "able to focus on something else",
            "can push it aside",
            "able to push it aside",
            "can move on",
            "thoughts go away",
            "thoughts gone",
            "they go away",
            "it doesn't bother me",
            "it dont bother me",
            "it doesn't bother me when",
            "don't bother me",
            "dont bother me",
            "if i make myself busy",
            "when i keep busy",
            "for that specific period of time",
            "i manage it",
            "i can manage it",
            "i manage these reactions",
            "i can manage these reactions",
            "i handle it",
            "i can handle it",
            "i handle these feelings",
            "i can handle these feelings",
            "i deal with it",
            "i can deal with it",
            "i cope with it",
            "i can cope with it",
            "i am able to manage",
            "i am able to control",
        ]

        # Check manageable phrases first.
        if any(
            phrase in answer
            for phrase in manageable_patterns
        ):
            evidence[attribute] = "manageable"

        elif any(
            phrase in answer
            for phrase in difficult_patterns
        ):
            evidence[attribute] = "difficult"

    # --------------------------------------------------------
    # 4. Persistence: How long does the thought continue?
    # --------------------------------------------------------
    elif attribute == "persistence":

        persistence = extract_persistence(answer)

        if persistence:
            evidence["persistence"] = persistence

    # Return evidence under the relevant construct.
        # --------------------------------------------------------
    # 5. Trigger: What situations or demands cause stress?
    # --------------------------------------------------------
    elif construct in {
    "stress_vulnerability",
    "emotional_reactivity",
}  and attribute == "trigger":

        # These words suggest that the user is describing
        # a situation, demand, or event that causes stress.
        trigger_patterns = [
            r"\bdeadline(s)?\b",
            r"\bfinal year project\b",
            r"\bproject\b",
            r"\bworkload\b",
            r"\btask(s)?\b",
            r"\bassignment(s)?\b",
            r"\bexam(s)?\b",
            r"\btest(s)?\b",
            r"\bcommittee\b",
            r"\bpresentation(s)?\b",
            r"\brequirement(s)?\b",
            r"\bresponsibilit(y|ies)\b",
            r"\btime pressure\b",
            r"\btime limit\b",
            r"\bwhen .* approach(es)?\b",
            r"\bwhen .* arrive(s)?\b",
            r"\bduring .* work\b",
            r"\bwhile .* working\b",
            r"\bbecause of\b",
            r"\bdue to\b",
            r"\bgrades?\b",
            r"\bresults?\b",
            r"\bconflict(s)?\b",
            r"\bargument(s)?\b",
            r"\bpressure\b",
            r"\bwhen .+\b",
            r"\bduring .+\b",
        ]

        if any(
            re.search(pattern, answer)
            for pattern in trigger_patterns
        ):
            # Remove conversational fillers while preserving
            # the user's original description.
            trigger = re.sub(
                r"^(yes|yeah|yep|like|well|actually)\s+",
                "",
                answer,
            ).strip()

            trigger = trigger.rstrip(".,!? ")

            if len(trigger.split()) >= 2:
                evidence["trigger"] = trigger
                # --------------------------------------------------------
    # 6. Functional impact: How does the experience affect
    #    everyday activities, work, studies, or relationships?
    # --------------------------------------------------------
    elif attribute == "functional_impact":

        no_impact_patterns = [
            r"\bno impact\b",
            r"\bno effect\b",
            r"\bdoesn't affect\b",
            r"\bdoes not affect\b",
            r"\bdoesn't interfere\b",
            r"\bdoes not interfere\b",
            r"\bnot affected\b",
            r"\bdoesn't change anything\b",
            r"\bdoes not change anything\b",
            r"\bnot affecting my daily life\b",
            r"\bdoesn't affect my daily life\b",
            r"\bdoes not affect my daily life\b",
            r"\bnot really\b",
            r"\bnot at all\b",
        ]

        impact_patterns = [
            r"\baffect(s|ed|ing)?\b",
            r"\bimpact(s|ed|ing)?\b",
            r"\binterfere(s|d|ing)?\b",
            r"\bstruggle with\b",
            r"\bdifficulty\b",
            r"\bhard to\b",
            r"\bfind it difficult\b",
            r"\bcan't focus\b",
            r"\bcannot focus\b",
            r"\bcan't concentrate\b",
            r"\bcannot concentrate\b",
            r"\blose concentration\b",
            r"\bavoid\b",
            r"\bwithdraw\b",
            r"\bmiss out\b",
            r"\bunable to\b",
            r"\bget in the way\b",
            r"\bproblems with\b",
            r"\btrouble with\b",
        ]

        if any(
            re.search(pattern, answer)
            for pattern in no_impact_patterns
        ):
            evidence["functional_impact"] = "none"

        elif any(
            re.search(pattern, answer)
            for pattern in impact_patterns
        ):
            # Preserve the user's original description.
            evidence["functional_impact"] = text.strip()
                # --------------------------------------------------------
    # 7. Recovery: How long does it take to return to the
    #    person's usual emotional state?
    # --------------------------------------------------------
    elif attribute == "recovery":

        recovery_patterns = [
            r"\bfeel normal again\b",
            r"\bback to normal\b",
            r"\breturn to normal\b",
            r"\bback to my usual self\b",
            r"\bfeel like myself again\b",
            r"\bback to my usual state\b",
            r"\breturn to my usual state\b",
            r"\bcalm down completely\b",
            r"\bget back to normal\b",
            r"\brecover\b",
            r"\brecovery\b",
        ]

        if any(
            re.search(pattern, answer)
            for pattern in recovery_patterns
        ):
            recovery_duration = extract_persistence(answer)

            if recovery_duration:
                evidence["recovery"] = recovery_duration
        
    # --------------------------------------------------------
    # 5. Emotional intensity: How strong is the reaction?
    # --------------------------------------------------------
    
    # --------------------------------------------------------
    # 8. Sensitivity: How easily does an emotional reaction occur?
    # --------------------------------------------------------
    elif construct == "emotional_reactivity" and attribute == "sensitivity":

        # Check negative responses first to avoid false positives.
        low_patterns = [
            r"\bnot easily upset\b",
            r"\bnot easily bothered\b",
            r"\bnot sensitive to small things\b",
            r"\bsmall things don't upset me\b",
            r"\bsmall things do not upset me\b",
            r"\bminor things don't bother me\b",
            r"\bminor things do not bother me\b",
            r"\bi rarely get upset over small things\b",
            r"\bi rarely get bothered by little things\b",
        ]

        high_patterns = [
            r"\beven small things\b",
            r"\bsmall things can upset me\b",
            r"\blittle things can upset me\b",
            r"\bminor things can upset me\b",
            r"\bget upset easily\b",
            r"\bgets upset easily\b",
            r"\beasily upset\b",
            r"\beasily bothered\b",
            r"\breact strongly to small things\b",
            r"\breact strongly to minor things\b",
            r"\bmore strongly than most people\b",
            r"\bmore sensitive than most people\b",
            r"\bvery sensitive\b",
            r"\bhighly sensitive\b",
            r"\boverreact to small things\b",
            r"\boverreact to minor things\b",
        ]

        moderate_patterns = [
            r"\bsomewhat sensitive\b",
            r"\boccasionally upset by small things\b",
            r"\bsometimes upset by small things\b",
            r"\bsometimes bothered by minor things\b",
            r"\bsometimes get upset by small things\b",
        ]

        if any(
            re.search(pattern, answer)
            for pattern in low_patterns
        ):
            evidence["sensitivity"] = "low"

        elif any(
            re.search(pattern, answer)
            for pattern in moderate_patterns
        ):
            evidence["sensitivity"] = "moderate"

        elif any(
            re.search(pattern, answer)
            for pattern in high_patterns
        ):
            evidence["sensitivity"] = "high"


    # --------------------------------------------------------
    # 6. Emotional intensity: How strong is the reaction?
    # --------------------------------------------------------
    elif construct == "emotional_reactivity" and attribute == "intensity":

        # Check low intensity first to avoid classifying
        # phrases such as "a little upset" as high.
        low_patterns = [
            r"\bnot very strong\b",
            r"\bnot that strong\b",
            r"\bnot intense\b",
            r"\bnot very upset\b",
            r"\bnot that upset\b",
            r"\bnot too upset\b",
            r"\bmild\b",
            r"\bslight\b",
            r"\ba little\b",
            r"\bslightly\b",
            r"\ba bit\b",
        ]

        moderate_patterns = [
            r"\bmoderate\b",
            r"\bmedium\b",
            r"\bmoderately strong\b",
            r"\bnoticeable\b",
            r"\bmoderately upsetting\b",
            r"\bsomewhat upsetting\b",
            r"\bsomewhat upset\b",
            r"\bmoderately upset\b",
        ]
        high_patterns = [
            r"\bvery strong\b",
            r"\bextremely strong\b",
            r"\bquite strong\b",
            r"\bvery intense\b",
            r"\bextremely intense\b",
            r"\bintense\b",
            r"\boverwhelming\b",
            r"\boverwhelmed\b",
            r"\bextremely overwhelmed\b",
            r"\bvery overwhelmed\b",
            r"\bvery overwhelming\b",
            r"\bdistressing\b",
            r"\bvery distressing\b",
            r"\bextremely distressing\b",
            r"\bso upset\b",
            r"\bvery upset\b",
            r"\breally upset\b",
            r"\bextremely upset\b",
            r"\bdeeply upset\b",
            r"\bfreak out\b",
            r"\bfreaking out\b",
            r"\bpanic attack(s)?\b",

            # Strong anxiety and nervousness
            r"\bvery anxious\b",
            r"\bextremely anxious\b",
            r"\bhighly anxious\b",
            r"\bseverely anxious\b",
            r"\bvery nervous\b",
            r"\bextremely nervous\b",
            r"\bhighly nervous\b",
        ]

        # Detect explicit denial before accepting high intensity.
        negated_patterns = [
            r"\b(?:don't|do not|doesn't|does not|didn't|did not|never|not)\s+(?:(?:feel|feeling|seem|seems|be|am|is|are)\s+)?(?:very\s+|really\s+|that\s+|extremely\s+|highly\s+|severely\s+|quite\s+)?(?:overwhelmed|overwhelming|distressed|distressing|upset|intense|anxious|nervous)\b",
        ]
        if any(re.search(p, answer) for p in low_patterns):
                 evidence["intensity"] = "low"

        elif any(re.search(p, answer) for p in negated_patterns):
            # Explicit denial means there is no positive
            # evidence of emotional intensity.
            pass

        elif any(re.search(p, answer) for p in moderate_patterns):
            evidence["intensity"] = "moderate"

        elif any(re.search(p, answer) for p in high_patterns):
            evidence["intensity"] = "high"

    if evidence:
        return {construct: evidence}

    return {}

# ============================================================
# 11. Main extraction function
# ============================================================

def extract_behavioral_evidence(text):
    """
    Extract behavioral evidence from a single user response.

    Parameters:
        text (str):
            The user's response.

    Returns:
        Dictionary containing detected constructs and attributes.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        return {}

    if is_explicit_worry_denial(text):
        return {"worry": {"detected": False}}
    
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        return {}

    result = {}

    worry = extract_worry_evidence(text)
    if worry:
        result["worry"] = worry

    rumination = extract_rumination_evidence(text)
    if rumination:
        result["rumination"] = rumination

    emotional_reactivity = extract_emotional_reactivity_evidence(text)
    if emotional_reactivity:
        result["emotional_reactivity"] = emotional_reactivity

    social_evaluation = extract_social_evaluation_evidence(text)
    if social_evaluation:
        result["social_evaluation"] = social_evaluation

    stress_vulnerability = extract_stress_vulnerability_evidence(text)
    if stress_vulnerability:
        result["stress_vulnerability"] = stress_vulnerability

    negative_self_evaluation = extract_negative_self_evaluation_evidence(text)
    if negative_self_evaluation:
        result["negative_self_evaluation"] = negative_self_evaluation

    # Repetitive Negative Thinking is a broader parent construct.
    if detect_repetition(text) and (
        "worry" in result or "rumination" in result
    ):
        result["repetitive_negative_thinking"] = {
            "detected": True,
            "repetition": True,
        }

    return result


# ============================================================
# 12. Simple test
# ============================================================

if __name__ == "__main__":

    test_responses = [
        "I keep worrying that I'll fail my presentation.",
        "After something embarrassing happens, I replay it over and over.",
        "I get overwhelmed very easily when I have too much work.",
        "I constantly worry about what other people think of me.",
        "I always feel like I'm not good enough.",
    ]

    for response in test_responses:

        print("\n" + "=" * 60)
        print("USER:", response)

        evidence = extract_behavioral_evidence(response)

        print("EVIDENCE:")
        print(evidence)