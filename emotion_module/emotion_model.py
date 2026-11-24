
from transformers import pipeline

from shared_utils.enrichment import generate_enriched_text
from shared_utils.compact_enrichment import generate_compact_enriched_text


# Load the same pretrained model for all experiments
classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)


def classify_text(text):

    results = classifier(text)[0]

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    predictions = []

    for item in results[:3]:

        predictions.append({
            "label": item["label"],
            "score": round(item["score"], 4)
        })

    return predictions


def detect_emotions(text):

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    # E1: Original text
    e1_predictions = classify_text(text)

    # E2: Detailed contextual enrichment
    e2_result = generate_enriched_text(text)
    e2_text = e2_result["enriched_text"]
    e2_predictions = classify_text(e2_text)

    # E3: Compact contextual enrichment
    e3_result = generate_compact_enriched_text(text)
    e3_text = e3_result["compact_enriched_text"]
    e3_predictions = classify_text(e3_text)

    return {
        "module": "emotion",

        "original_text": text,

        "experiments": {
            "E1_original": {
                "input_text": text,
                "predictions": e1_predictions
            },

            "E2_detailed_enrichment": {
                "input_text": e2_text,
                "predictions": e2_predictions
            },

            "E3_compact_enrichment": {
                "input_text": e3_text,
                "predictions": e3_predictions,
                "context_phrases": e3_result["context_phrases"]
            }
        },

        "enrichment_metadata": e2_result["metadata"]
    }
