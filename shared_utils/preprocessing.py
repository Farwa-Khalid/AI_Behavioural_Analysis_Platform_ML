from shared_utils.emoji_mapper import replace_emojis
from shared_utils.slang_mapper import replace_slang

def preprocess_text(text):

    text = replace_emojis(text)

    text = replace_slang(text)

    return text