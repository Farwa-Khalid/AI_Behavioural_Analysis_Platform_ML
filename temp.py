from shared_utils.slang_mapper import detect_slang, normalize_slang


text = "ngl brooooo I am cooked fr, idk what to do rn"


print("DETECTED SLANG:")
print(detect_slang(text))


print("\nNORMALIZED TEXT:")
print(normalize_slang(text))