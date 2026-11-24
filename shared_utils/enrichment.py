
from collections import Counter

from shared_utils.preprocessing import preprocess_text
from shared_utils.context_processor import interpret_context


def generate_enriched_text(text):

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    # Step 1: Get detection results
    preprocessing_result = preprocess_text(text)

    # Step 2: Get contextual interpretations
    context_result = interpret_context(text)

    slang_results = context_result["slang_interpretations"]
    emoji_results = context_result["emoji_interpretations"]

    # Step 3: Count repeated emojis
    emoji_counts = Counter(
        item["emoji"]
        for item in preprocessing_result["emoji_matches"]
    )

    # Step 4: Build contextual annotations
    annotations = []

    # Process slang interpretations
    for item in slang_results:

        if item["selected_interpretation"] is not None:

            annotation = (
                f"Slang '{item['term']}' means "
                f"{item['selected_interpretation']}."
            )

            annotations.append(annotation)

    # Process emoji interpretations
    processed_emojis = set()

    for item in emoji_results:

        emoji_character = item["emoji"]

        # Avoid repeating the same annotation
        if emoji_character in processed_emojis:
            continue

        processed_emojis.add(emoji_character)

        count = emoji_counts[emoji_character]

        selected_meaning = item["selected_interpretation"]

        if selected_meaning is not None:

            annotation = (
                f"Emoji {emoji_character} indicates "
                f"{selected_meaning}."
            )

            annotations.append(annotation)

        else:

            annotation = (
                f"Emoji {emoji_character} has ambiguous meaning."
            )

            annotations.append(annotation)

        # Preserve emoji repetition as an intensity-related cue
        if count > 1:

            annotations.append(
               
                f"Emoji {emoji_character} was repeated "
                f"{count} times, which may indicate emphasis or intensity."
            )

    # Step 5: Generate enriched representation
    if annotations:

        contextual_information = " ".join(annotations)

        enriched_text = (
            f"{text} "
            f"Contextual information: {contextual_information}"
        )

    else:

        enriched_text = text

    # Step 6: Return original and enriched information
    return {
        "original_text": text,
        "enriched_text": enriched_text,
        "metadata": {
            "slang_interpretations": slang_results,
            "emoji_interpretations": emoji_results,
            "emoji_counts": dict(emoji_counts),
            "annotations": annotations
        }
    }
