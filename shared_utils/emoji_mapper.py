# import emoji

# GENZ_MAP = {
#     ":skull:": " shocked overwhelmed",
#     ":loudly_crying_face:": " emotional crying ",
#     ":face_with_tears_of_joy:": " laughing amusement ",
#     ":fire:": " amazing exciting ",
#     ":red_heart:": " love affection ",
#     ":enraged_face:": " anger furious "
# }

# def replace_emojis(text):

#     text = emoji.demojize(text)

#     for emoji_code, meaning in GENZ_MAP.items():
#         text = text.replace(emoji_code, meaning)

#     return text

import emoji


GENZ_EMOJI_MAP = {
    "💀": [
        "shocked",
        "overwhelmed",
        "laughing",
        "disbelief"
    ],

    "😭": [
        "crying",
        "emotional",
        "laughing",
        "frustration",
        "disbelief"
    ],

    "😂": [
        "laughing",
        "amusement"
    ],

    "🔥": [
        "amazing",
        "exciting",
        "excellent"
    ],

    "❤️": [
        "love",
        "affection"
    ],

    "😡": [
        "anger",
        "frustration"
    ],

    "🙏": [
        "please",
        "gratitude",
        "hope",
        "request"
    ],

    "🤡": [
        "foolish",
        "embarrassing",
        "self-mockery"
    ],

    "🗿": [
        "deadpan",
        "stoic",
        "absurd reaction"
    ],

    "👀": [
        "watching",
        "interested",
        "suspicious"
    ],

    "✨": [
        "emphasis",
        "excitement",
        "aesthetic emphasis"
    ],

    "💅": [
        "confidence",
        "attitude",
        "emphasis"
    ],

    "🥲": [
        "emotional",
        "bittersweet",
        "pretending to be okay"
    ]
}


def detect_emojis(text):
    """
    Detect emojis present in the original text.

    Returns:
        A list of dictionaries containing:
        - emoji
        - possible meanings
        - count
    """

    if not isinstance(text, str):
        return []

    detected = []

    emoji_items = emoji.emoji_list(text)

    for item in emoji_items:

        emoji_character = item["emoji"]

        # Only add emojis that we have specifically
        # defined Gen-Z interpretations for.
        if emoji_character in GENZ_EMOJI_MAP:

            detected.append({
                "emoji": emoji_character,
                "possible_meanings": GENZ_EMOJI_MAP[
                    emoji_character
                ]
            })

    return detected


def count_emojis(text):
    """
    Count each supported Gen-Z emoji in the text.
    """

    if not isinstance(text, str):
        return {}

    counts = {}

    emoji_items = emoji.emoji_list(text)

    for item in emoji_items:

        emoji_character = item["emoji"]

        if emoji_character in GENZ_EMOJI_MAP:

            counts[emoji_character] = (
                counts.get(emoji_character, 0) + 1
            )

    return counts


def analyze_emojis(text):
    """
    Analyze emoji presence and repetition.

    Returns:
        A dictionary containing:
        - detected_emojis
        - emoji_counts
        - repeated_emojis
        - emoji_intensity
    """

    if not isinstance(text, str):
        return {
            "detected_emojis": [],
            "emoji_counts": {},
            "repeated_emojis": [],
            "emoji_intensity": "none"
        }

    detected = detect_emojis(text)
    counts = count_emojis(text)

    repeated = []

    for emoji_character, count in counts.items():

        if count > 1:
            repeated.append({
                "emoji": emoji_character,
                "count": count
            })

    total_count = sum(counts.values())

    if total_count == 0:
        intensity = "none"

    elif total_count == 1:
        intensity = "single"

    elif total_count <= 3:
        intensity = "moderate"

    else:
        intensity = "high"

    return {
        "detected_emojis": detected,
        "emoji_counts": counts,
        "repeated_emojis": repeated,
        "emoji_intensity": intensity
    }


def replace_emojis(text):
    """
    Backward-compatible emoji replacement function.

    This function is kept temporarily so existing project code
    does not break.

    It converts only our known emojis into their possible
    meanings rather than forcing one fixed interpretation.
    """

    if not isinstance(text, str):
        return text

    result = text

    for emoji_character, meanings in GENZ_EMOJI_MAP.items():

        meaning_text = " ".join(meanings)

        result = result.replace(
            emoji_character,
            f" {meaning_text} "
        )

    return result