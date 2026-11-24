
from shared_utils.enrichment import generate_enriched_text


print("\n========== TEXT ENRICHMENT TEST ==========")

text = input("\nEnter text: ")

try:

    result = generate_enriched_text(text)

    print("\nOriginal Text:")
    print(result["original_text"])

    print("\nEnriched Text:")
    print(result["enriched_text"])

    print("\nEmoji Counts:")
    print(result["metadata"]["emoji_counts"])

    print("\nContextual Annotations:")

    for annotation in result["metadata"]["annotations"]:
        print("-", annotation)

except (TypeError, ValueError) as error:

    print("Input Error:", error)
