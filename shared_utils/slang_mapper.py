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