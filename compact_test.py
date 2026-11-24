
from shared_utils.compact_enrichment import generate_compact_enriched_text
from pprint import pprint

text = "I have an exam tomorrow and I am cooked 😭😭😭"

result = generate_compact_enriched_text(text)

print("\n========== COMPACT ENRICHMENT TEST ==========")

print("\nOriginal Text:")
print(result["original_text"])

print("\nE3 Enriched Text:")
print(result["compact_enriched_text"])

print("\nContext Phrases:")
pprint(result["context_phrases"])
