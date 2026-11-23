
import json
import emoji
from pathlib import Path


# Locate the emoji JSON file
MAPPING_FILE = (
    Path(__file__).parent / "mappings" / "emojis.json"
)


# Load Gen Z emoji interpretations
def load_emoji_map():

    with open(MAPPING_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Emoji JSON must contain an object.")

    return data


GENZ_MAP = load_emoji_map()


# Detect emojis in text
def detect_emojis(text):

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    detected_emojis = []

    emoji_matches = emoji.emoji_list(text)

    for match in emoji_matches:

        emoji_character = match["emoji"]

        shortcode = emoji.demojize(
            emoji_character,
            language="en"
        )

        standard_meaning = (
            shortcode.strip(":").replace("_", " ")
        )

        genz_meanings = GENZ_MAP.get(
            emoji_character,
            []
        )

        detected_emojis.append({
            "emoji": emoji_character,
            "shortcode": shortcode,
            "standard_meaning": standard_meaning,
            "genz_interpretations": genz_meanings,
            "start": match["match_start"],
            "end": match["match_end"]
        })

    return detected_emojis

