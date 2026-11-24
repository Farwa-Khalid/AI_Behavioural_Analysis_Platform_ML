
import json
from pathlib import Path

base = Path("shared_utils/mappings")

with open(base / "slang.json", encoding="utf-8") as f:
    slang_data = json.load(f)

with open(base / "emojis.json", encoding="utf-8") as f:
    emoji_data = json.load(f)

with open(base / "context_rules.json", encoding="utf-8") as f:
    rules = json.load(f)


# Check that contextual slang exists in slang.json
missing_slang = (
    set(rules["slang_terms"]) - set(slang_data)
)

# Check that contextual emojis exist in emojis.json
missing_emojis = (
    set(rules["emoji_terms"]) - set(emoji_data)
)

# Check that all group references exist
invalid_slang_groups = [
    group for group in rules["slang_terms"].values()
    if group not in rules["slang_groups"]
]

invalid_emoji_groups = [
    group for group in rules["emoji_terms"].values()
    if group not in rules["emoji_groups"]
]

print("\n========== MAPPING VALIDATION ==========")

print("Total slang dictionary entries:", len(slang_data))
print("Contextual slang mappings:", len(rules["slang_terms"]))

print("Total emoji dictionary entries:", len(emoji_data))
print("Contextual emoji mappings:", len(rules["emoji_terms"]))

print("\nMissing slang:", missing_slang)
print("Missing emojis:", missing_emojis)
print("Invalid slang groups:", invalid_slang_groups)
print("Invalid emoji groups:", invalid_emoji_groups)

if not any([
    missing_slang,
    missing_emojis,
    invalid_slang_groups,
    invalid_emoji_groups
]):
    print("\nSUCCESS: All contextual mappings are valid.")
else:
    print("\nERROR: Please fix the mapping issues.")
