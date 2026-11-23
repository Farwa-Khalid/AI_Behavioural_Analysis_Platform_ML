
"""
Knowledge retriever — baseline implementation.

Searches the existing Markdown knowledge base and returns
relevant passages with their source filenames.

This is a lexical retrieval baseline, not yet vector-based RAG.
"""

from pathlib import Path
import re


# knowledge_retriever.py is inside rag/retrieval/
RAG_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = RAG_DIR / "knowledge_base"



def tokenize(text):
    """Convert text into meaningful lowercase word tokens."""

    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by",
        "can", "do", "does", "for", "from", "how", "i",
        "in", "is", "it", "me", "my", "of", "on", "or",
        "the", "their", "them", "there", "this", "to",
        "was", "we", "what", "when", "where", "which",
        "who", "why", "will", "with", "you", "your"
    }

    tokens = set(re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower()))

    return tokens - stop_words



def load_documents():
    """Load all Markdown documents from the knowledge base."""

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {KNOWLEDGE_BASE_DIR}"
        )

    documents = []

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")

        if content.strip():
            documents.append({
                "source": path.name,
                "content": content,
            })

    return documents


def retrieve_documents(query, top_k=3):
    """
    Return the most relevant documents using keyword overlap.

    Args:
        query: Search question or assessment objective.
        top_k: Maximum number of documents to return.

    Returns:
        Ranked list of dictionaries containing source,
        score, and content.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    documents = load_documents()
    ranked = []

    for document in documents:
        document_tokens = tokenize(document["content"])

        overlap = query_tokens & document_tokens

        if not overlap:
            continue

        # Baseline score: fraction of query terms found in document.
        score = len(overlap) / len(query_tokens)

        ranked.append({
            "source": document["source"],
            "score": round(score, 4),
            "content": document["content"],
        })

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked[:top_k]


if __name__ == "__main__":
    query = (
        "How difficult is it to shift attention away "
        "from repetitive worry?"
    )

    results = retrieve_documents(query, top_k=3)

    print("QUERY:", query)
    print("=" * 70)

    for index, result in enumerate(results, start=1):
        print(f"\nRESULT {index}")
        print("Source:", result["source"])
        print("Score:", result["score"])
        print("Content preview:")
        print(result["content"][:500])
        print("-" * 70)
