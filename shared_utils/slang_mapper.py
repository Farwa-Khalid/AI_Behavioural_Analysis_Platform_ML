
import json
import re
from pathlib import Path


# JSON mapping location
MAPPING_FILE = (
    Path(__file__).parent / "mappings" / "slang.json"
)


# Load and validate slang knowledge
def load_slang_map():

    with open(MAPPING_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Slang JSON must contain an object.")

    for term, meanings in data.items():

        if not isinstance(term, str) or not term.strip():
            raise ValueError("Invalid slang term in JSON.")

        if (
            not isinstance(meanings, list)
            or not meanings
            or not all(
                isinstance(item, str) and item.strip()
                for item in meanings
            )
        ):
            raise ValueError(
                f"Invalid or empty meanings for slang: {term}"
            )

    return data


SLANG_MAP = load_slang_map()


# Compile one expression, prioritizing longer phrases
def build_slang_pattern():

    terms = sorted(
        SLANG_MAP.keys(),
        key=len,
        reverse=True
    )

    escaped_terms = [
        re.escape(term)
        for term in terms
    ]

    combined_pattern = "|".join(escaped_terms)

    return re.compile(
        rf"(?<!\w)(?:{combined_pattern})(?!\w)",
        re.IGNORECASE
    )


SLANG_PATTERN = build_slang_pattern()


# Detect slang without overlapping matches
def detect_slang(text):

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    detected_slang = []

    for match in SLANG_PATTERN.finditer(text):

        normalized_term = match.group().lower()

        detected_slang.append({
            "term": match.group(),
            "normalized_term": normalized_term,
            "possible_meanings": SLANG_MAP[normalized_term],
            "start": match.start(),
            "end": match.end()
        })

    return detected_slang
