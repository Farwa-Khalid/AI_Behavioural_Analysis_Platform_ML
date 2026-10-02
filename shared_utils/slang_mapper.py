SLANG_MAP = {
    "cooked": "overwhelmed stressed exhausted",
    "bro": "friend",
    "fr": "for real",
    "idk": "i do not know",
    "ngl": "not gonna lie",
    "rn": "right now",
    "lowkey": "slightly",
    "highkey": "definitely",
    "wtf": "what the hell",
    "lmao": "laughing"
}

def replace_slang(text):

    words = text.split()

    converted = []

    for word in words:

        cleaned = word.lower()

        if cleaned in SLANG_MAP:
            converted.append(SLANG_MAP[cleaned])
        else:
            converted.append(word)

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