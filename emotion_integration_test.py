
from emotion_module.emotion_model import detect_emotions

from pprint import pprint


print("\n========== EMOTION INTEGRATION TEST ==========")

text = input("\nEnter text: ")

try:

    result = detect_emotions(text)

    print("\nOriginal Text:")
    print(result["original_text"])

    print("\nEnriched Text:")
    print(result["enriched_text"])

    print("\nOriginal Emotion Predictions:")
    pprint(result["original_predictions"])

    print("\nEnhanced Emotion Predictions:")
    pprint(result["enhanced_predictions"])

    print("\nContextual Annotations:")

    for annotation in result["enrichment_metadata"]["annotations"]:
        print("-", annotation)

except (TypeError, ValueError) as error:

    print("\nInput Error:", error)
