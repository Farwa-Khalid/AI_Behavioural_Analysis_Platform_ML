
"""
Passage-level knowledge retriever.

Splits Markdown documents into sections and ranks
individual sections using keyword overlap.
"""

import re
from rag.retrieval.knowledge_retriever import load_documents, tokenize
def split_into_passages(document):
    """Split a Markdown document at second-level headings."""

    content = document["content"]
    source = document["source"]

    # Split before headings such as: ## 1. What Is Worry?
    sections = re.split(r"(?m)(?=^##\s+)", content)

    passages = []

    for index, section in enumerate(sections, start=1):
        section = section.strip()

        if not section:
            continue

        # Extract the heading, if one exists.
        heading_match = re.match(r"^##\s+(.+)", section)
        heading = heading_match.group(1).strip().lower() if heading_match else ""

        # Exclude sections that contain only source/reference information.
        excluded_headings = {
            "source",
            "sources",
            "references",
            "bibliography",
        }

        if heading in excluded_headings:
            continue

        # Ignore sections containing only whitespace or stop words.
        if not tokenize(section):
            continue

        passages.append({
            "source": source,
            "passage_id": index,
            "content": section,
        })

    return passages



def retrieve_passages(query, top_k=3):
    """Return the top matching sections from the knowledge base."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    documents = load_documents()
    passages = []

    for document in documents:
        passages.extend(split_into_passages(document))

    ranked = []

    for passage in passages:
        passage_tokens = tokenize(passage["content"])
        overlap = query_tokens & passage_tokens

        if not overlap:
            continue

        score = len(overlap) / len(query_tokens)

        ranked.append({
            **passage,
            "score": round(score, 4),
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

    results = retrieve_passages(query, top_k=3)

    print("QUERY:", query)
    print("=" * 70)

    for rank, result in enumerate(results, start=1):
        print(f"\nRESULT {rank}")
        print("Source:", result["source"])
        print("Passage ID:", result["passage_id"])
        print("Score:", result["score"])
        print("Passage:")
        print(result["content"][:700])
        print("-" * 70)
