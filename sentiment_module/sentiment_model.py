from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def detect_sentiment(text):

    result = classifier(text)[0]

    return {
        "module": "sentiment",

        "predictions": [
            {
                "label": result["label"],
                "score": round(result["score"], 4)
            }
        ]
    }