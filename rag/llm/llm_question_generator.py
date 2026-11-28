import os
import re
import difflib

from google import genai
from google.genai import types

import os
from dotenv import load_dotenv

"""
LLM Question Generator

Purpose:
    Generate one neutral follow-up question using:
    1. The objective selected by the adaptive controller.
    2. Relevant passages retrieved from the knowledge base.

Important:
    Gemini phrases the question.
    The adaptive controller decides what evidence is needed.
"""

load_dotenv()

from rag.retrieval.semantic_retriever import (
    retrieve_semantic_passages,
)


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)


SYSTEM_INSTRUCTION = """
You generate follow-up questions for an adaptive,
research-oriented behavioural assessment.

The assessment may examine different behavioural
constructs, including:

- Worry
- Rumination
- Emotional reactivity
- Stress vulnerability
- Social evaluation
- Negative self-evaluation

Rules:

- Generate exactly ONE question.
- Follow the supplied construct and attribute.
- Understand the selected construct before generating
  the question.
- Use wording appropriate to that construct.
- For emotional reactivity, ask about emotional reactions
  and feelings, not worrying thoughts.
- For worry, ask about worries and future-oriented concerns.
- For rumination, ask about repetitive thoughts.
- For stress vulnerability, ask about responses to stress.
- Use clear, natural, neutral language.
- Use retrieved passages as background guidance.
- Do not diagnose the user or assign personality scores.
- Do not assume that a behaviour is present.
- Avoid leading, judgmental, or emotionally loaded wording.
- Do not repeat information the user has already provided.
- Output only one question, without explanations or headings.
"""

def generate_fallback_question(objective):
    """
    Generate a neutral fallback question based on the
    controller-selected construct and attribute.
    """

    if isinstance(objective, dict):
        construct = str(
            objective.get("construct", "")
        ).lower()

        attribute = str(
            objective.get("attribute", "")
        ).lower()

        objective_text = str(
            objective.get("objective", "")
        ).lower()

    else:
        construct = ""
        objective_text = str(objective).lower()
        attribute = ""

    # Infer the attribute if it was not supplied.
    if not attribute:

        if "trigger" in objective_text:
            attribute = "trigger"

        elif "intensity" in objective_text or "strongly" in objective_text:
            attribute = "intensity"

        elif "persistence" in objective_text or "how long" in objective_text:
            attribute = "persistence"

        elif "frequency" in objective_text or "how often" in objective_text:
            attribute = "frequency"

        elif "repetition" in objective_text or "return" in objective_text:
            attribute = "repetition"

        elif "controllability" in objective_text or "control" in objective_text:
            attribute = "controllability"

        elif "switching" in objective_text or "redirect" in objective_text:
            attribute = "switching_difficulty"

        elif "functional impact" in objective_text or "interfere" in objective_text:
            attribute = "functional_impact"

        elif "recovery" in objective_text:
            attribute = "recovery"

        elif "sensitivity" in objective_text:
            attribute = "sensitivity"

    # Construct-specific wording.
    experiences = {
        "emotional_reactivity": "these emotional reactions",
        "worry": "these worries",
        "rumination": "these recurring thoughts",
        "repetitive_negative_thinking": "these repetitive negative thoughts",
        "stress_vulnerability": "these stress-related experiences",
        "social_evaluation": "these concerns about being judged",
        "negative_self_evaluation": "these self-critical thoughts",
    }

    experience = experiences.get(
        construct,
        "these experiences"
    )

    # Questions are selected using both construct and attribute.
    fallback_questions = {

        "trigger": (
            f"What specific situations tend to bring on {experience}?"
        ),

        "intensity": (
            f"How intense or distressing do {experience} become for you?"
        ),

        "persistence": (
            f"Once {experience} begin, approximately how long do they last?"
        ),

        "frequency": (
            f"How many times do {experience} come up "
            "during a typical day or week?"
        ),

        "repetition": (
            f"Do {experience} repeatedly return even after you try to move on?"
        ),

        "controllability": (
            f"How difficult is it for you to manage or control {experience}?"
        ),

        "switching_difficulty": (
            f"How difficult is it to shift your attention away from {experience}?"
        ),

        "functional_impact": (
            f"How much do {experience} affect your everyday activities, studies, or sleep?"
        ),

        "recovery": (
            f"After {experience} affect you, "
            "approximately how long does it take you to feel like yourself again?"
        ),

        "sensitivity": (
            "How easily do you experience strong emotional reactions, "
            "including in response to relatively small or minor situations?"
        ),
    }

    return fallback_questions.get(
        attribute,
        "Could you tell me a little more about how this experience affects you?"
    )

def is_question_aligned_with_objective(question, objective):
    """
    Check whether a generated question contains clear indicators
    of the controller-selected assessment attribute.

    Returns:
        True  -> question appears aligned.
        False -> question should be replaced by a fallback.
    """

    if not isinstance(question, str) or not question.strip():
        return False

    if not isinstance(objective, dict):
        return False

    construct = objective.get("construct", "").lower().strip()
    attribute = objective.get("attribute", "").lower().strip()
    question = question.lower().strip()
    
        # Reject questions that clearly ask about another attribute.
    conflicting_patterns = {
        "controllability": [
            r"\bhow often\b",
            r"\bhow frequently\b",
            r"\bhow many times\b",
        ],
    }

    for pattern in conflicting_patterns.get(attribute, []):

        if re.search(pattern, question):
            return False
    # Construct-specific wording validation.
    construct_patterns = {

        "worry": [
            r"\bworr(?:y|ies|ied|ying)\b",
            r"\bconcerns?\b",
            r"\bwhat if\b",
            r"\bfuture events\b",
        ],

        "rumination": [
            r"\brepetitive thoughts?\b",
            r"\brepeated thoughts?\b",
            r"\brecurring thoughts?\b",
            r"\bsame thoughts\b",
            r"\bthoughts return\b",
            r"\bthinking about past experiences\b",
            r"\brevisiting previous experiences\b",
            r"\brepeatedly revisiting\b",
            r"\bgoing over past events\b",
            r"\bkeep thinking about\b",
            r"\bthinking about the same thing\b",
        ],

        "emotional_reactivity": [
            r"\bemotional reactions?\b",
            r"\bemotions?\b",
            r"\bfeelings?\b",
            r"\bstrong emotional\b",
        ],

        "stress_vulnerability": [
            r"\bstress\b",
            r"\bstressful situations?\b",
            r"\bstress responses?\b",
            r"\bunder pressure\b",
        ],

        "social_evaluation": [
            r"\bbeing judged\b",
            r"\bjudg(?:e|ed|es|ing|ment)\b",
            r"\bothers? are judging\b",
            r"\bcritic(?:ism|ized|ised|ize|ise)\b",
            r"\bevaluat(?:e|ed|es|ing|ion)\b",
            r"\bnegative(?:ly)? perceived\b",
            r"\bwhat others think of you\b",
            r"\bothers' opinions\b",
        ],

        "negative_self_evaluation": [
            r"\bself-critical\b",
            r"\bnegative beliefs about yourself\b",
            r"\bnegative view of yourself\b",
            r"\bshortcomings\b",
            r"\bfeelings of inadequacy\b",
            r"\bcriticize yourself\b",
            r"\bcriticise yourself\b",
            r"\bself-criticism\b",
            r"\bblame yourself\b",
            r"\bthink negatively about yourself\b",
            r"\bnegative thoughts about yourself\b",
        ],
    }

    # Reject unknown constructs.
    if construct not in construct_patterns:
        return False

    # Reject questions that do not mention the selected construct.
    if not any(
        re.search(pattern, question)
        for pattern in construct_patterns[construct]
    ):
        return False
    # Attribute-specific phrases that indicate alignment.
    alignment_patterns = {

        "trigger": [
            r"\bwhat situations\b",
            r"\bwhat specific situations\b",
            r"\bwhat events\b",
            r"\bwhat demands\b",
            r"\bwhat circumstances\b",
            r"\bwhat tends to cause\b",
            r"\bwhat brings on\b",
            r"\bwhat specific aspects\b.*\btend to bring on\b",
            r"\bwhat brings about\b",
            r"\bwhat bring about\b",
            r"\bwhat triggers\b",
            r"\bwhat sparks\b",
            r"\bwhen does\b",
            r"\bwhat leads to\b",
            r"\bwhat tends to lead to\b",
            r"\bwhat brings about feelings of\b",
            r"\bwhich situations\b",
            r"\bwhich circumstances\b",
            r"\bwhich events\b",
            r"\bwhich demands\b",
            r"\bwhich circumstances tend to trigger\b",
            r"\bwhich situations tend to trigger\b",
            r"\bwhat kinds of situations\b",
            r"\bwhat kinds of circumstances\b",
            r"\bwhat types of situations\b",
            r"\bwhat types of circumstances\b",
            r"\bwhat kinds of events\b",
            r"\bwhat specific types of situations\b",
        ],


            "intensity": [
                r"\bhow strong\b",
                r"\bhow strongly\b",
                r"\bhow intense\b",
                r"\bhow distressing\b",
                r"\bhow overwhelming\b",
                r"\bhow severe\b",
],

        "persistence": [
            r"\bhow long\b",
            r"\bhow much time\b",
            r"\bhow long do\b",
            r"\bhow long does\b",
            r"\bhow long are\b",
        ],

        "recovery": [
            r"\bfeel like yourself again\b",
            r"\breturn to normal\b",
            r"\bback to normal\b",
            r"\busual emotional state\b",
            r"\bfeel back to your usual state\b",
            r"\breturn to your usual state\b",
            r"\brecover\b",
            r"\bafter an emotional reaction\b",
        ],

        "sensitivity": [
            r"\bhow easily\b",
            r"\bhow readily\b",
            r"\bhow minor\b",
            r"\bsmall or minor\b",
            r"\bsmall situations\b",
            r"\bminor situations\b",
            r"\bsensitive\b",
            r"\beasily upset\b",
        ],

        "frequency": [
            r"\bhow often\b",
            r"\bhow frequently\b",
            r"\bhow many times\b",
        ],

            "repetition": [
                r"\bkeep returning\b",
                r"\bcome back repeatedly\b",
                r"\breturn again\b",
                r"\bsame thoughts\b",
                r"\bkeep coming back\b",
                r"\brepeatedly revisiting\b",
                r"\brevisit(?:ing)? previous experiences\b",
                r"\bgo over (?:the same|past) experiences repeatedly\b",
                r"\bthink about (?:the same thing|past experiences) repeatedly\b",
                r"\brepeatedly return\b",
            ],

        "controllability": [
                r"\bcontrol\b",
                r"\bmanage\b",
                r"\bregulate\b",
                r"\bhandle\b",
                r"\bcope with\b",
                r"\bmanageable\b",
                r"\bhow manageable\b",
                r"\bset (?:them|it|these|those) aside\b",
                r"\bput (?:them|it|these|those) aside\b",
                r"\blet go of\b",
                r"\bability to control\b",
                r"\bdifficult to manage\b",
                r"\beasy to manage\b",
                r"\bstop these thoughts\b",
                r"\bmanage these thoughts\b",
                r"\bmanage your reactions\b",
                r"\bcontrol your reactions\b",
                r"\bregulate your emotions\b",
                r"\bmanage your emotions\b",
                r"\bcontrol your emotions\b",
            ],



        "switching_difficulty": [
            r"\bshift your attention\b",
            r"\bredirect your attention\b",
            r"\bswitch your attention\b",
            r"\bmove your attention\b",
            r"\bmove on from these thoughts\b",
        ],

        "functional_impact": [
            r"\baffect your everyday\b",
            r"\binterfere with\b",
            r"\bimpact your\b",
            r"\baffect your studies\b",
            r"\baffect your work\b",
            r"\baffect your relationships\b",
        ],

        "temporal_orientation": [
            r"\bpast, present, or future\b",
            r"\brelate to the past\b",
            r"\brelate to the future\b",
            r"\babout the past\b",
            r"\babout the future\b",
        ],

        "negative_outcome": [
            r"\bwhat outcome\b",
            r"\bwhat might happen\b",
            r"\bwhat are you afraid\b",
            r"\bwhat do you fear\b",
        ],

        "perceived_likelihood": [
            r"\bhow likely\b",
            r"\bchances of\b",
            r"\bprobability\b",
        ],

        "perceived_severity": [
            r"\bhow serious\b",
            r"\bhow severe would\b",
            r"\bhow bad would\b",
        ],

        "perceived_coping": [
            r"\bhow capable\b",
            r"\bhandle the situation\b",
            r"\bcope with\b",
            r"\bmanage the outcome\b",
        ],
    }

    # Reject attributes for which no validation rules exist.
    if attribute not in alignment_patterns:
        return False

    # Check whether the question contains at least one
    # indicator associated with the selected attribute.
    for pattern in alignment_patterns[attribute]:

        if re.search(pattern, question):
            return True

    return False
def is_question_repetitive(
    question,
    conversation_history,
    threshold=0.65,
):
    """
    Check whether a generated question closely resembles
    a question previously asked by the assistant.

    Only previous assistant questions are considered.
    """

    if not question or not conversation_history:
        return False

    def normalize_question(text):
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    current_question = normalize_question(question)

    if not current_question:
        return False

    for turn in conversation_history:

        if not isinstance(turn, dict):
            continue

        role = turn.get("role", "").lower()

        if role != "assistant":
            continue

        previous_question = normalize_question(
            turn.get("text", "")
        )

        if not previous_question:
            continue

        similarity = difflib.SequenceMatcher(
            None,
            current_question,
            previous_question,
        ).ratio()

        if similarity >= threshold:
            return True

    return False

def generate_non_repeated_fallback_question(
    objective,
    conversation_history=None,
):
    """
    Generate an aligned fallback question that has not
    already been asked in the conversation.

    The existing fallback is attempted first.
    An alternative is used if the original is repeated.
    Returns None if no suitable question is available.
    """

    if not isinstance(objective, dict):
        return None

    construct = objective.get("construct")
    attribute = objective.get("attribute")

    if not construct or not attribute:
        return None

    # --------------------------------------------------------
    # 1. Define construct-specific experiences
    # --------------------------------------------------------

    experiences = {
        "emotional_reactivity": "these emotional reactions",
        "worry": "these worries",
        "rumination": "these recurring thoughts",
        "repetitive_negative_thinking": (
            "these repetitive negative thoughts"
        ),
        "stress_vulnerability": (
            "these stress-related experiences"
        ),
        "social_evaluation": (
            "these concerns about being judged"
        ),
        "negative_self_evaluation": (
            "these self-critical thoughts"
        ),
    }

    experience = experiences.get(construct)

    if not experience:
        return None

    # --------------------------------------------------------
    # 2. Define alternative wording for each supported
    #    fallback attribute
    # --------------------------------------------------------

    alternatives = {

        "trigger": (
            "In what kinds of circumstances do you notice "
            "your stress levels rising?"
        ),

        "intensity": (
            "How overwhelming can these feelings become "
            "at their peak?"
        ),

        "persistence": (
            f"How much time do {experience} usually occupy "
            "once they begin?"
        ),

        "frequency": (
            f"How frequently do you notice {experience} "
            "occurring in your everyday life?"
        ),

        "repetition": (
            "Do these recurring thoughts keep coming back?"
        ),

        "controllability": (
            "How manageable are these worries for you?"
        ),

        "switching_difficulty": (
            "How easily can you move your attention to "
            "another activity when worries arise?"
        ),

        "functional_impact": (
            "Do these emotional reactions interfere with "
            "your ability to complete daily tasks or "
            "responsibilities?"
        ),
        "recovery": (
            f"Once {experience} have passed, "
            "how long does it usually take you to feel back to your usual state?"
        ),

        "sensitivity": (
            "How readily do you experience strong reactions "
            "related to these emotional reactions?"
        ),
    }
    alternative_question = alternatives.get(attribute)

    # --------------------------------------------------------
    # 3. Try the existing fallback first
    # --------------------------------------------------------

    candidates = [
        generate_fallback_question(objective)
    ]

    # Add the alternative if this attribute supports one.
    if alternative_question:
        candidates.append(alternative_question)

    # --------------------------------------------------------
    # 4. Validate every candidate and reject repetitions
    # --------------------------------------------------------

    for candidate in candidates:

        if not candidate:
            continue

        is_aligned = is_question_aligned_with_objective(
            candidate,
            objective,
        )

        if not is_aligned:
            continue

        is_repeated = is_question_repetitive(
            candidate,
            conversation_history,
        )

        if is_repeated:
            continue

        return candidate

    # No aligned, non-repeated candidate was available.
    return None

def generate_follow_up_question(
    objective,
    retrieved_passages,
    current_concern=None,
    latest_response=None,
    conversation_history=None,
):
    """
    Generate a context-aware question for a controller-selected
    assessment objective.

    Gemini must assess only the selected construct and attribute.
    Generated questions are validated for alignment and repetition.
    """

    # =========================================================
    # 1. VALIDATE AND READ THE SELECTED OBJECTIVE
    # =========================================================

    if isinstance(objective, dict):

        construct = objective.get("construct", "")
        attribute = objective.get("attribute", "")
        objective_description = objective.get("objective", "")

        if not construct or not attribute or not objective_description:
            raise ValueError(
                "Objective must contain construct, attribute, and objective."
            )

    elif isinstance(objective, str) and objective.strip():

        # Backward compatibility for older callers.
        construct = "Not supplied"
        attribute = "Not supplied"
        objective_description = objective

    else:
        raise ValueError(
            "objective must be a non-empty string or objective dictionary."
        )

    # =========================================================
    # 2. NON-REPEATED FALLBACK HELPER
    # =========================================================

    def get_non_repeated_fallback():

        if isinstance(objective, dict):

            return generate_non_repeated_fallback_question(
                objective,
                conversation_history,
            )

        # Preserve backward compatibility for string objectives.
        return generate_fallback_question(objective)

    # =========================================================
    # 3. CHECK API KEY
    # =========================================================

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        print(
            "\nGemini API key is unavailable. "
            "Trying a non-repeated fallback question."
        )

        return get_non_repeated_fallback()

    # =========================================================
    # 4. VALIDATE RETRIEVED PASSAGES
    # =========================================================

    if not retrieved_passages:
        raise ValueError(
            "At least one retrieved passage is required."
        )

    context_parts = []

    for passage in retrieved_passages[:3]:

        source = passage.get("source", "Unknown source")
        content = passage.get("content", "")

        if isinstance(content, str) and content.strip():

            context_parts.append(
                f"Source: {source}\n{content[:1500]}"
            )

    if not context_parts:
        raise ValueError(
            "Retrieved passages contain no usable content."
        )

    knowledge_context = "\n\n---\n\n".join(context_parts)

    # =========================================================
    # 5. PREPARE CONVERSATION HISTORY
    # =========================================================

    history_lines = []

    if conversation_history:

        for turn in conversation_history[-6:]:

            if isinstance(turn, dict):

                text = turn.get("text", "")
                role = turn.get("role", "User")

                history_lines.append(
                    f"{role}: {text}"
                )

            elif isinstance(turn, str):

                history_lines.append(turn)

    history_context = (
        "\n".join(history_lines)
        if history_lines
        else "No previous conversation supplied."
    )

    # =========================================================
    # 6. PREPARE USER CONTEXT
    # =========================================================

    concern = (
        current_concern.strip()
        if isinstance(current_concern, str)
        and current_concern.strip()
        else "Not explicitly identified."
    )

    latest = (
        latest_response.strip()
        if isinstance(latest_response, str)
        and latest_response.strip()
        else "Not supplied."
    )

    # =========================================================
    # 7. CONSTRUCT THE GEMINI PROMPT
    # =========================================================

    prompt = f"""
You are generating one follow-up question for a behavioural
assessment.

The assessment controller has already selected the objective.
You MUST follow the selected construct and attribute exactly.

SELECTED CONSTRUCT:
{construct}

SELECTED ATTRIBUTE:
{attribute}

OBJECTIVE DESCRIPTION:
{objective_description}

USER'S CURRENT CONCERN:
{concern}

LATEST USER RESPONSE:
{latest}

RECENT CONVERSATION:
{history_context}

RETRIEVED KNOWLEDGE:
{knowledge_context}

RULES FOR GENERATING THE QUESTION:

1. ASSESS ONLY THE SELECTED ATTRIBUTE.
   Never substitute another attribute.
   The controller will select the next objective separately.

2. The selected attribute is authoritative.
   Generate a question specifically about that attribute.

3. Understand the selected attribute in the context of the
   selected construct.

   The meaning of an attribute must remain appropriate to
   the type of experience being assessed.

   CONSTRUCT-SPECIFIC GUIDANCE:

   - emotional_reactivity:
     Focus on emotional reactions, feelings, and responses
     to situations. Do not describe these experiences as
     worrying or repetitive thoughts unless the user has
     explicitly mentioned thoughts.

   - worry:
     Focus on concerns, anticipated negative outcomes,
     uncertainty, and future-oriented worries.

   - rumination:
     Focus on repeatedly thinking about experiences,
     events, or concerns, particularly when thoughts are
     difficult to move on from.

   - stress_vulnerability:
     Focus on how the person responds to stressful
     situations and how stress affects their functioning.

   - social_evaluation:
     Focus on concerns about being judged, criticized,
     evaluated, or negatively perceived by others.

   - negative_self_evaluation:
     Focus on self-critical thoughts, negative beliefs
     about oneself, and perceived personal shortcomings.

   ATTRIBUTE DEFINITIONS:

   - trigger:
     The specific situation, event, or circumstance that
     brings about the selected experience.

   - intensity:
     How strong or distressing the selected experience
     becomes.

   - persistence:
     How long the selected experience continues.

   - recovery:
     How long it takes the person to return to their usual
     state after the selected experience.

   - sensitivity:
     How readily or easily the person responds to relevant
     situations or circumstances.

   - frequency:
     How often the selected experience occurs across time.

   - repetition:
     Whether the same thought, concern, or experience
     repeatedly returns.

   - controllability:
     How difficult or easy it is to manage, regulate,
     or stop the selected experience when it occurs.
     For emotional reactivity, focus on managing emotional
     reactions rather than stopping thoughts.

   - switching_difficulty:
     How difficult it is to redirect attention away from
     the selected experience.
     Use thought-related wording for worry and rumination,
     and reaction-related wording for emotional reactivity.

   - functional_impact:
     How the selected experience affects everyday
     activities, studies, work, sleep, or relationships.

   - temporal_orientation:
     Whether the concern relates to the past, present,
     or future.

   - negative_outcome:
     The unwanted outcome the person fears.

   - perceived_likelihood:
     How likely the person thinks the feared outcome is.

   - perceived_severity:
     How serious the feared outcome seems.

   - perceived_coping:
     How capable the person feels of handling the feared
     outcome.

4. Keep the question specific to the user's actual concern.
   Do not invent another event or situation.

5. Ask ONE clear question about ONE main attribute.
   Do not combine intensity with persistence.
   Do not combine persistence with recovery.
   Do not combine controllability with switching difficulty.

6. Respect information already given in the conversation.
   Do not ask the user to repeat an answer already provided.

7. Interpret short answers in context.
   Do not assume that yes or no answers an attribute unless
   the previous question makes its meaning clear.

8. If the latest response is unrelated, ask one brief,
   gentle clarification connected to the selected attribute.
   Do not introduce a different assessment attribute.

9. Do not repeatedly rephrase a question without gaining
   new information.

10. Do not diagnose the user or assign personality scores.
    Retrieved knowledge is background guidance, not a reason
    to lecture the user.

OUTPUT:
Return exactly one concise, natural question.
Return only the question, without headings or explanations.
"""

    # =========================================================
    # 8. GENERATE AND VALIDATE QUESTION USING GEMINI
    # =========================================================

    try:

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=100,
            ),
        )

        question = (response.text or "").strip()

        if not question:
            raise RuntimeError(
                "Gemini returned an empty question."
            )

        # -----------------------------------------------------
        # 8A. CHECK OBJECTIVE ALIGNMENT
        # -----------------------------------------------------

        is_aligned = is_question_aligned_with_objective(
            question,
            objective,
        )

        if not is_aligned:

            print("\nGEMINI GENERATED QUESTION:")
            print(question)

            print(
                "\nGenerated question does not match the "
                f"selected attribute: {attribute}"
            )

            print(
                "Trying a non-repeated fallback question."
            )

            return get_non_repeated_fallback()

        # -----------------------------------------------------
        # 8B. CHECK FOR REPETITIVE QUESTIONS
        # -----------------------------------------------------

        if is_question_repetitive(
            question,
            conversation_history,
        ):

            print("\nGEMINI GENERATED QUESTION:")
            print(question)

            print(
                "\nGemini generated a question that was "
                "already asked."
            )

            print(
                "Trying a non-repeated fallback question."
            )

            return get_non_repeated_fallback()

        # -----------------------------------------------------
        # 8C. RETURN VALID, NON-REPEATED QUESTION
        # -----------------------------------------------------

        return question

    # =========================================================
    # 9. HANDLE GEMINI ERRORS
    # =========================================================

    except Exception as error:

        print(
            f"\nGemini question generation failed: {error}"
        )

        print(
            "Trying a non-repeated fallback question."
        )

        return get_non_repeated_fallback()
