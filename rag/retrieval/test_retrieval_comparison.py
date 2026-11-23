
from rag.retrieval.semantic_retriever import retrieve_semantic_passages

from rag.retrieval.passage_retriever import retrieve_passages

TEST_QUERIES = [
    "How difficult is it to stop worrying?",
    "How strongly does a person react emotionally to stressful events?",
    "Does the person worry about being judged or criticized by others?",
    "Do negative thoughts keep returning during other activities?",
]


def print_results(method_name, results):
    print(f"\n{method_name}")

    if not results:
        print("No matching passages found.")
        return

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['source']} | "
            f"Passage {result['passage_id']} | "
            f"Score: {result['score']}"
        )
        print(result["content"][:180].replace("\n", " "))
        print()


def main():
    for query in TEST_QUERIES:
        print("\n" + "=" * 80)
        print("QUERY:", query)
        print("=" * 80)

        keyword_results = retrieve_passages(query, top_k=3)
        semantic_results = retrieve_semantic_passages(query, top_k=3)

        print_results("KEYWORD RETRIEVAL", keyword_results)
        print_results("SEMANTIC RETRIEVAL", semantic_results)


if __name__ == "__main__":
    main()
