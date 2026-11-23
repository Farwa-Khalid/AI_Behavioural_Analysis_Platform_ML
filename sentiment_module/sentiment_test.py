import sys
import os
import json

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from sentiment_model import detect_sentiment
from sentiment_model import explain_sentiment
from shared_utils.preprocessing import preprocess_text

text = input("Enter text: ")

processed_text = preprocess_text(text)

print("Original:", text)
print("Processed:", processed_text)

print("\n--- Prediction ---")
print(detect_sentiment(processed_text))

print("\n--- Explanation ---")
result = explain_sentiment(processed_text)
print(json.dumps(result, indent=2))
print("\n", result["summary"])