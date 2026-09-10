from neuroticism_model import predict_neuroticism


test_texts = [
    "I keep worrying about everything that could go wrong.",
    "I feel calm and confident about my plans.",
    "Sometimes I overthink things that happened in the past."
]


print("=" * 60)
print("NEUROTICISM MODEL TEST")
print("=" * 60)


for text in test_texts:

    result = predict_neuroticism(text)

    print("\nText:", text)
    print("Prediction:", result["prediction"])
    print("Confidence:", result["confidence"], "%")
    print("Neurotic probability:", result["neurotic_probability"], "%")
    print("Non-neurotic probability:", result["non_neurotic_probability"], "%")


print("\n" + "=" * 60)
print("✅ NEUROTICISM MODEL TEST COMPLETED")
print("=" * 60)