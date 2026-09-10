from detoxify import Detoxify

model = Detoxify("original")

def detect_toxicity(text):

    results = model.predict(text)

    predictions = []

    for label, score in results.items():

        predictions.append({
            "label": label,
            "score": round(float(score), 4)
        })

    predictions = sorted(
        predictions,
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "module": "toxicity",
        "predictions": predictions
    }