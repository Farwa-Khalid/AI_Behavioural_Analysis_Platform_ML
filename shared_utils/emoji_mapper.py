import emoji

GENZ_MAP = {
    ":skull:": " shocked overwhelmed",
    ":loudly_crying_face:": " emotional crying ",
    ":face_with_tears_of_joy:": " laughing amusement ",
    ":fire:": " amazing exciting ",
    ":red_heart:": " love affection ",
    ":enraged_face:": " anger furious "
}

def replace_emojis(text):

    text = emoji.demojize(text)

    for emoji_code, meaning in GENZ_MAP.items():
        text = text.replace(emoji_code, meaning)

    return text