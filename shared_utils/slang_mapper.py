
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
    return " ".join(converted)


# import re


# SLANG_MAP = {
#     "cooked": {
#         "type": "ambiguous",
#         "possible_meanings": [
#             "overwhelmed",
#             "stressed",
#             "exhausted",
#             "in trouble",
#             "unable to succeed"
#         ]
#     },

#     "bro": {
#         "type": "informal",
#         "meaning": "friend / person"
#     },

#     "fr": {
#         "type": "abbreviation",
#         "meaning": "for real"
#     },

#     "idk": {
#         "type": "abbreviation",
#         "meaning": "I do not know"
#     },

#     "ngl": {
#         "type": "abbreviation",
#         "meaning": "not gonna lie"
#     },

#     "rn": {
#         "type": "abbreviation",
#         "meaning": "right now"
#     },

#     "lowkey": {
#         "type": "informal",
#         "meaning": "slightly / somewhat"
#     },

#     "highkey": {
#         "type": "informal",
#         "meaning": "definitely / openly"
#     },

#     "wtf": {
#         "type": "abbreviation",
#         "meaning": "what the hell"
#     },

#     "lmao": {
#         "type": "internet_expression",
#         "meaning": "laughing"
#     },

#     "imo": {
#         "type": "abbreviation",
#         "meaning": "in my opinion"
#     },

#     "tbh": {
#         "type": "abbreviation",
#         "meaning": "to be honest"
#     },

#     "brb": {
#         "type": "abbreviation",
#         "meaning": "be right back"
#     },

#     "irl": {
#         "type": "abbreviation",
#         "meaning": "in real life"
#     },

#     "sus": {
#         "type": "slang",
#         "meaning": "suspicious"
#     },

#     "goated": {
#         "type": "slang",
#         "meaning": "excellent / highly praised"
#     },

#     "ate": {
#         "type": "slang",
#         "meaning": "did something extremely well"
#     },

#     "cringe": {
#         "type": "slang",
#         "meaning": "embarrassing / awkward"
#     },

#     "gonna": {
#         "type": "informal",
#         "meaning": "going to"
#     },

#     "wanna": {
#         "type": "informal",
#         "meaning": "want to"
#     },

#     "gotta": {
#         "type": "informal",
#         "meaning": "have to"
#     },

#     "lemme": {
#         "type": "informal",
#         "meaning": "let me"
#     },

#     "cuz": {
#         "type": "informal",
#         "meaning": "because"
#     },

#     "bc": {
#         "type": "abbreviation",
#         "meaning": "because"
#     },

#     "u": {
#         "type": "abbreviation",
#         "meaning": "you"
#     },

#     "ur": {
#         "type": "abbreviation",
#         "meaning": "your / you are"
#     },

#     "tho": {
#         "type": "informal",
#         "meaning": "though"
#     }
# }


# def detect_slang(text):
#     """
#     Detect slang/informal terms in text.

#     Returns a list containing information about each detected term.
#     """

#     if not isinstance(text, str):
#         return []

#     detected = []

#     # Find word-like tokens while keeping punctuation outside the token.
#     tokens = re.findall(r"\b[\w']+\b", text.lower())

#     for token in tokens:

#         if token in SLANG_MAP:

#             entry = {
#                 "term": token,
#                 "type": SLANG_MAP[token]["type"]
#             }

#             if "meaning" in SLANG_MAP[token]:
#                 entry["meaning"] = SLANG_MAP[token]["meaning"]

#             if "possible_meanings" in SLANG_MAP[token]:
#                 entry["possible_meanings"] = SLANG_MAP[token][
#                     "possible_meanings"
#                 ]

#             detected.append(entry)

#     return detected


# def normalize_slang(text):
#     """
#     Create a lightly normalized version of the text.

#     Important:
#     This does NOT aggressively replace slang.
#     The original text should always be preserved separately.
#     """

#     if not isinstance(text, str):
#         return text

#     normalized = text

#     replacements = {
#         "fr": "for real",
#         "ngl": "not gonna lie",
#         "idk": "i do not know",
#         "rn": "right now",
#         "imo": "in my opinion",
#         "tbh": "to be honest",
#         "brb": "be right back",
#         "irl": "in real life",
#         "bc": "because",
#         "cuz": "because",
#         "gonna": "going to",
#         "wanna": "want to",
#         "gotta": "have to",
#         "lemme": "let me",
#         "tho": "though"
#     }

#     for slang, replacement in replacements.items():

#         pattern = rf"\b{re.escape(slang)}\b"

#         normalized = re.sub(
#             pattern,
#             replacement,
#             normalized,
#             flags=re.IGNORECASE
#         )

#     return normalized
