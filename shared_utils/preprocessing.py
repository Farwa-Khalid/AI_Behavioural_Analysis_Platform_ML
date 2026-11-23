
from shared_utils.emoji_mapper import detect_emojis
from shared_utils.slang_mapper import detect_slang


def preprocess_text(text):

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    # Detect slang
    slang_matches = detect_slang(text)

    # Detect emojis
    emoji_matches = detect_emojis(text)

    # Return structured detection information
    return {
        "original_text": text,
        "slang_matches": slang_matches,
        "emoji_matches": emoji_matches
    }
