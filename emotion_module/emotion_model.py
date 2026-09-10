from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)

def detect_emotions(text):

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

    return {
        "module": "emotion",
        "predictions": predictions
    }