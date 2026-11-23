
from shared_utils.enrichment import generate_enriched_text


def generate_compact_enriched_text(text):

    # Step 1: Reuse existing contextual interpretation
    result = generate_enriched_text(text)

    metadata = result["metadata"]

    context_phrases = []

    # Step 2: Collect slang meanings
    for item in metadata["slang_interpretations"]:

        meaning = item.get("selected_interpretation")

        if meaning:

            # Avoid overlapping general meanings
            if "overwhelmed" in meaning.lower():
                continue

            if meaning not in context_phrases:
                context_phrases.append(meaning)

    # Step 3: Collect emoji meanings
    for item in metadata["emoji_interpretations"]:

        meaning = item.get("selected_interpretation")

        if meaning:

            if "overwhelmed" in meaning.lower():
                continue

            if meaning not in context_phrases:
                context_phrases.append(meaning)

    # Step 4: Detect academic stress
    stress_keywords = {
        "exam", "exams", "test", "tests",
        "assignment", "assignments",
        "deadline", "deadlines",
        "homework", "studying", "study"
    }

    matched_keywords = set()

    for item in metadata["slang_interpretations"]:
        matched_keywords.update(
            word.lower()
            for word in item.get("matched_keywords", [])
        )

    for item in metadata["emoji_interpretations"]:
        matched_keywords.update(
            word.lower()
            for word in item.get("matched_keywords", [])
        )

    if matched_keywords.intersection(stress_keywords):
        context_phrases.append("academic stress")

    # Step 5: Detect repeated emojis
    repeated_emojis = [
        emoji_character
        for emoji_character, count
        in metadata["emoji_counts"].items()
        if count > 1
    ]

    if repeated_emojis:
        context_phrases.append("repeated emoji emphasis")

    # Step 6: Generate compact text
    if context_phrases:

        compact_context = ", ".join(context_phrases)

        compact_text = (
            f"{text} Context: {compact_context}."
        )

    else:
        compact_text = text

    return {
        "original_text": text,
        "compact_enriched_text": compact_text,
        "context_phrases": context_phrases,
        "metadata": metadata
    }
