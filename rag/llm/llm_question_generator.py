
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

import os

from google import genai
from google.genai import types

import os
from dotenv import load_dotenv

load_dotenv()

from rag.retrieval.semantic_retriever import (
    retrieve_semantic_passages,
)


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)


SYSTEM_INSTRUCTION = """
You generate follow-up questions for a research-oriented
behavioural assessment concerning worry and related patterns.

Rules:
- Generate exactly ONE question.
- Use clear, natural, neutral language.
- Ask only about the supplied assessment objective.
- Use the retrieved passages as background guidance.
- Do not diagnose the user or assign personality scores.
- Do not assume that a behaviour is present.
- Avoid leading, judgmental, or emotionally loaded wording.
- Do not repeat information the user has already provided.
- Output only the question, without explanations or headings.
"""


def generate_follow_up_question(
    objective,
    retrieved_passages,
    current_concern=None,
    latest_response=None,
    conversation_history=None,
):
    """
    Generate a context-aware question for a controller-selected objective.

    Gemini phrases the question using the user's concern and
    conversation history. The adaptive controller still decides
    which evidence should be collected next.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set in the environment."
        )

    if not isinstance(objective, str) or not objective.strip():
        raise ValueError(
            "objective must be a non-empty string."
        )

    if not retrieved_passages:
        raise ValueError(
            "At least one retrieved passage is required."
        )

    # Prepare retrieved knowledge.
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

    # Prepare recent conversation history.
    history_lines = []

    if conversation_history:
        for turn in conversation_history[-6:]:
            if isinstance(turn, dict):
                text = turn.get("text", "")
                role = turn.get("role", "User")
                history_lines.append(f"{role}: {text}")
            elif isinstance(turn, str):
                history_lines.append(turn)

    history_context = (
        "\n".join(history_lines)
        if history_lines
        else "No previous conversation supplied."
    )

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

  
    prompt = f"""
You are generating one follow-up question for a behavioural
assessment. The assessment controller has already selected
the objective. You MUST follow it exactly.

SELECTED ASSESSMENT OBJECTIVE:
{objective}

USER'S CURRENT CONCERN:
{concern}

LATEST USER RESPONSE:
{latest}

RECENT CONVERSATION:
{history_context}

RETRIEVED KNOWLEDGE:
{knowledge_context}

RULES FOR GENERATING THE QUESTION:

1. ASSESS ONLY THE SELECTED OBJECTIVE.
   Do not switch to a different behavioural attribute.
   The controller will choose the next objective separately.

2. Use these definitions to distinguish objectives:
   - temporal orientation: whether the concern relates to the
     past, present, or future.
   - frequency: how often the thoughts occur across time.
   - repetition: whether the same thought or worry returns.
   - persistence: how long the thoughts last once they begin.
   - controllability: whether the person can stop or manage
     the thoughts when they want to.
   - switching difficulty: how difficult it is to redirect
     attention away from the thoughts.
   - functional impact: whether the thoughts interfere with
     everyday activities, sleep, study, work, or relationships.
   - intensity: how emotionally strong or distressing the
     experience feels.
   - negative outcome: what unwanted outcome the person fears.
   - perceived likelihood: how likely the person thinks the
     feared outcome is.
   - perceived severity: how serious the feared outcome seems.
   - perceived coping: how capable the person feels of handling
     the feared outcome.
   - uncertainty: how difficult it is to tolerate not knowing
     what will happen.

3. Keep the question specific to the user's actual concern.
   For example, if the concern is about people's past behaviour,
   refer to those memories rather than inventing another event.

4. Ask ONE clear question about ONE main attribute.
   Do not combine persistence and controllability in one question.
   Do not ask several alternatives or multiple questions at once.

5. Respect information already given in the conversation.
   Do not ask the user to repeat an answer they have clearly
   provided. Use the history to phrase the next question naturally.

6. Interpret short answers in context, but do not assume that
   "yes" or "no" answers an attribute unless the previous
   question makes its meaning clear.

7. If the latest response is unrelated to the assessment,
   do not pretend it answers the selected objective. Ask one
   brief, gentle clarification connected to the original concern.
   Do not introduce a new assessment attribute.

8. Do not repeatedly rephrase a question that has already been
   asked without gaining new information. If the conversation
   shows that the user cannot answer, acknowledge this briefly
   and allow the assessment controller to handle the next step.

9. Do not diagnose the user or assign personality scores.
   Retrieved knowledge is background guidance, not a reason
   to lecture the user.

OUTPUT:
Return exactly one concise, natural question.
Return only the question, without headings or explanations.
"""


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

    return question
