import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from rag.assessment.assessment_state import CONSTRUCTS


load_dotenv()

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)


SYSTEM_INSTRUCTION = """
You are a behavioural evidence extraction assistant.

Your task is to interpret a user's response and identify possible
behavioural evidence relevant to the allowed assessment constructs.

STRICT RULES:

1. Use only information supported by the user's original response.
2. Do not diagnose the user or assign a personality score.
3. Do not assume that ordinary workload, assignments, or busy
   schedules automatically indicate stress or neuroticism.
4. Recognize understandable spelling mistakes, informal wording,
   and alternative expressions.
5. Use evidence_state "known" only when the user's words explicitly
   support the interpretation.
6. Use evidence_state "uncertain" when an interpretation is plausible
   but needs clarification.
7. Do not turn a possible interpretation into confirmed evidence.
8. The evidence_text field must be an exact quotation copied from
   the user's original response.
9. Do not invent frequency, duration, intensity, persistence,
   controllability, or functional impact.
10. If the response does not provide enough information, return
    an empty evidence list and ask a neutral clarification question.
11. Return valid JSON only. Do not include Markdown or explanations.

Required JSON structure:

{
  "evidence": [
    {
      "construct": "stress_vulnerability",
      "attribute": "detected",
      "value": true,
      "evidence_state": "known",
      "evidence_text": "exact words from the response"
    }
  ],
  "clarification_question": null
}

The construct and attribute must come from the allowed schema.
The value must be a string, number, or boolean.
The evidence_state must be "known" or "uncertain".
"""


def _get_allowed_schema():
    """
    Return the constructs and attributes currently supported
    by the assessment state.
    """
    return {
        construct: list(attributes)
        for construct, attributes in CONSTRUCTS.items()
    }


def _empty_result(status, original_response, error=None):
    """
    Return a consistent result when extraction cannot be completed.
    """
    result = {
        "status": status,
        "original_response": original_response,
        "evidence": [],
        "clarification_question": None,
    }

    if error:
        result["error"] = error

    return result


def _parse_json_response(response_text):
    """
    Parse JSON returned by Gemini.

    Also handles a response accidentally wrapped in Markdown fences.
    """
    if not isinstance(response_text, str) or not response_text.strip():
        raise ValueError("Gemini returned an empty response.")

    cleaned = response_text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return json.loads(cleaned)


def _validate_evidence(raw_evidence, original_response):
    """
    Keep only evidence that follows the assessment schema
    and contains a supporting quotation from the original response.
    """
    if not isinstance(raw_evidence, list):
        return []

    allowed_schema = _get_allowed_schema()

    validated = []
    seen = set()

    for item in raw_evidence:

        if not isinstance(item, dict):
            continue

        construct = item.get("construct")
        attribute = item.get("attribute")
        value = item.get("value")
        evidence_state = item.get("evidence_state")
        evidence_text = item.get("evidence_text")

        # Check construct and attribute.
        if construct not in allowed_schema:
            continue

        if attribute not in allowed_schema[construct]:
            continue

        # Only accept supported evidence states.
        if evidence_state not in {"known", "uncertain"}:
            continue

        # Do not accept empty or unsupported values.
        if value is None or not isinstance(
            value,
            (str, int, float, bool),
        ):
            continue

        # Require an exact supporting quotation.
        if not isinstance(evidence_text, str):
            continue

        if not evidence_text.strip():
            continue

        if evidence_text.casefold() not in original_response.casefold():
            continue

        # Avoid duplicate evidence records.
        key = (
            construct,
            attribute,
            str(value),
            evidence_state,
            evidence_text.casefold(),
        )

        if key in seen:
            continue

        seen.add(key)

        validated.append({
            "construct": construct,
            "attribute": attribute,
            "value": value,
            "evidence_state": evidence_state,
            "evidence_text": evidence_text,
        })

    return validated


def extract_semantic_evidence(
    user_response,
    conversation_context=None,
):
    """
    Interpret a user response using Gemini.

    This function does not update assessment state.
    It only returns candidate evidence for later review.

    Parameters
    ----------
    user_response : str
        The user's original response.

    conversation_context : str, optional
        A short description of the preceding conversation.

    Returns
    -------
    dict
        Extraction status, original response, validated evidence,
        and an optional clarification question.
    """

    if not isinstance(user_response, str):
        raise TypeError("user_response must be a string.")

    original_response = user_response.strip()

    if not original_response:
        return _empty_result(
            "no_input",
            original_response,
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return _empty_result(
            "unavailable",
            original_response,
            "GEMINI_API_KEY is not configured.",
        )

    allowed_schema = _get_allowed_schema()

    context = conversation_context or "No additional context provided."

    prompt = f"""
Interpret the following user response.

ALLOWED ASSESSMENT SCHEMA:
{json.dumps(allowed_schema, indent=2)}

PREVIOUS CONVERSATION CONTEXT:
{context}

USER'S ORIGINAL RESPONSE:
{original_response}

Return JSON with exactly these top-level fields:

- evidence: a list of evidence objects
- clarification_question: a neutral question or null

Each evidence object must contain:

- construct
- attribute
- value
- evidence_state ("known" or "uncertain")
- evidence_text (an exact quotation from the original response)

Important interpretation guidance:

- A clear spelling variation such as "stressfull" may express
  "stressful". If the meaning is clear, identify the relevant
  evidence, but quote the original spelling in evidence_text.
- A phrase such as "workload" may describe a possible trigger.
  Do not assume it proves stress vulnerability by itself.
- Thinking about consequences may suggest future-oriented concern,
  but do not assume that it is worry unless the response supports it.
- If the user gives several fragments, interpret them in the
  context of the preceding conversation, but do not invent details.
- Use "uncertain" when the interpretation needs confirmation.
- If no supported evidence can be identified, return an empty list
  and ask one useful, neutral clarification question.
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,
                max_output_tokens=700,
                response_mime_type="application/json",
            ),
        )

        parsed = _parse_json_response(response.text)

    except Exception as exc:
        print("Gemini semantic evidence extraction failed:", exc)

        return _empty_result(
            "unavailable",
            original_response,
            str(exc),
        )

    if not isinstance(parsed, dict):
        return _empty_result(
            "invalid_response",
            original_response,
            "Gemini response was not a JSON object.",
        )

    evidence = _validate_evidence(
        parsed.get("evidence", []),
        original_response,
    )

    clarification = parsed.get("clarification_question")

    if not isinstance(clarification, str):
        clarification = None
    else:
        clarification = clarification.strip() or None

    # Stress-vulnerability evidence safeguard

    has_repeated_pattern = bool(
        re.search(
            r"\b(every day|daily|often|frequently|regularly|repeatedly|all the time|most of the time|keeps happening|whenever I face|whenever I experience)\b",
            original_response,
            re.IGNORECASE,
        )
    )

    has_general_coping_difficulty = bool(
        re.search(
            r"\b(struggle|struggling|have difficulty|find it difficult|find it hard|unable|cannot|can't)\b.{0,50}\b(cope|coping|manage|managing|handling|handle|recover)\b|\b(difficulty|difficulties)\b.{0,35}\b(coping|managing|handling|recovering)\b",
            original_response,
            re.IGNORECASE,
        )
    )

    if not (has_repeated_pattern and has_general_coping_difficulty):
        for item in evidence:
            if (
                item["construct"] == "stress_vulnerability"
                and item["attribute"] == "detected"
                and item["value"] is True
                and item["evidence_state"] == "known"
            ):
                item["evidence_state"] = "uncertain"
                clarification = (
                    "Does this kind of stress happen repeatedly "
                    "in your life, or is it mainly related to "
                    "this particular situation?"
                )

    return {
        "status": "ok" if evidence else "no_evidence",
        "original_response": original_response,
        "evidence": evidence,
        "clarification_question": clarification,
    }
    
