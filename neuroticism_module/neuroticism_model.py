# import os
# import joblib
# from sentence_transformers import SentenceTransformer

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MODEL_PATH = os.path.join(BASE_DIR, "neurotic_model.pkl")

# model = joblib.load(MODEL_PATH)

# embedder = SentenceTransformer("all-mpnet-base-v2")


# def predict_neuroticism(text):
#     embedding = embedder.encode([text])

#     probabilities = model.predict_proba(embedding)[0]
#     prediction = model.predict(embedding)[0]

#     return {
#         "prediction": "Neurotic" if prediction == 1 else "Non-Neurotic",
#         "confidence": round(max(probabilities) * 100, 2),
#         "neurotic_probability": round(probabilities[1] * 100, 2),
#         "non_neurotic_probability": round(probabilities[0] * 100, 2)
#     }

import os
import joblib
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "neurotic_model.pkl"
)

EMBEDDER_DIR = os.path.join(
    BASE_DIR,
    "mpnet_embedder",
    "mpnet_embedder"
)


# Load trained classifier
model = joblib.load(MODEL_PATH)


# Load the exact saved MPNet embedder used for the model
embedder = SentenceTransformer(EMBEDDER_DIR)


def predict_neuroticism(text):
    """
    Predict neuroticism from a single text input.
    """

    embedding = embedder.encode(
        [text],
        convert_to_numpy=True
    )

    probabilities = model.predict_proba(embedding)[0]
    prediction = model.predict(embedding)[0]

    return {
        "prediction": "Neurotic" if prediction == 1 else "Non-Neurotic",
        "confidence": round(float(max(probabilities)) * 100, 2),
        "neurotic_probability": round(float(probabilities[1]) * 100, 2),
        "non_neurotic_probability": round(float(probabilities[0]) * 100, 2)
    }