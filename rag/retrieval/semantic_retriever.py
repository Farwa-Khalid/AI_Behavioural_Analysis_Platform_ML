
"""
Semantic passage retriever for the AI Behavioural Analysis Platform.

Uses the existing local MPNet model to retrieve knowledge-base
passages according to cosine similarity.
"""

from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from rag.retrieval.passage_retriever import split_into_passages
from rag.retrieval.knowledge_retriever import load_documents

# Resolve paths from this file, not from the terminal's current directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "neuroticism_module"
    / "mpnet_embedder"
    / "mpnet_embedder"
)

# Load the existing model locally. Do not download missing files.
model = SentenceTransformer(
    str(MODEL_PATH),
    local_files_only=True,
)


# Cache passage data and embeddings for reuse.
_CACHED_PASSAGES = None
_CACHED_EMBEDDINGS = None


def get_passage_index():
    """Load and embed passages only once per Python process."""

    global _CACHED_PASSAGES, _CACHED_EMBEDDINGS

    if _CACHED_PASSAGES is None:
        _CACHED_PASSAGES = load_passages()

        passage_texts = [
            passage["content"] for passage in _CACHED_PASSAGES
        ]

        if passage_texts:
            _CACHED_EMBEDDINGS = model.encode(
                passage_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        else:
            _CACHED_EMBEDDINGS = np.empty((0, 768))

    return _CACHED_PASSAGES, _CACHED_EMBEDDINGS


def load_passages():
    """Split all knowledge-base documents into sections."""

    passages = []

    for document in load_documents():
        passages.extend(split_into_passages(document))

    return passages


def retrieve_semantic_passages(query, top_k=3):
    """
    Retrieve passages using cosine similarity between embeddings.

    Returns dictionaries containing source, passage_id,
    similarity score, and passage content.
    """

    # 1. Validate the query.
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    # 2. Validate the number of results.
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    # 3. Get cached passages and their embeddings.
    passages, passage_embeddings = get_passage_index()

    # 4. Stop if there are no passages.
    if not passages:
        return []

    # 5. Convert the user's query into an embedding.
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    # 6. Calculate cosine similarity.
    # Normalized vectors: dot product equals cosine similarity.
    scores = passage_embeddings @ query_embedding

    # 7. Sort passages from highest to lowest similarity.
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    # 8. Build the results.
    results = []

    for index in ranked_indices:
        result = dict(passages[int(index)])
        result["score"] = round(float(scores[index]), 4)
        results.append(result)

    # 9. Return the best-matching passages.
    return results

if __name__ == "__main__":
    query = "How difficult is it to stop worrying?"

    print("QUERY:", query)
    print("=" * 70)

    results = retrieve_semantic_passages(query, top_k=3)

    for rank, result in enumerate(results, start=1):
        print(f"\nRESULT {rank}")
        print("Source:", result["source"])
        print("Passage ID:", result["passage_id"])
        print("Cosine similarity:", result["score"])
        print("Passage:")
        print(result["content"][:600])
        print("-" * 70)
