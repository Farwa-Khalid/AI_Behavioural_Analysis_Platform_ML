from shared_utils.emoji_mapper import (
    detect_emojis,
    analyze_emojis
)


text = "I have three assignments tomorrow 😭💀💀"


print("DETECTED EMOJIS:")
print(detect_emojis(text))


print("\nEMOJI ANALYSIS:")
print(analyze_emojis(text))