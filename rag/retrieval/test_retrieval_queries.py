
from passage_retriever import retrieve_passages


TEST_QUERIES = [
    {
        "name": "Difficulty controlling worry",
        "query": "How difficult is it to stop worrying?",
    },
    {
        "name": "Emotional reaction",
        "query": "How strongly does a person react emotionally to stressful events?",
    },
    {
        "name": "Social evaluation",
        "query": "Does the person worry about being judged or criticized by others?",
    },
    {
        "name": "Repeated negative thoughts",
        "query": "Do negative thoughts keep returning during other activities?",
    },
]


for test in TEST_QUERIES:
    print("\n" + "=" * 70)
    print("TEST:", test["name"])
    print("QUERY:", test["query"])

    results = retrieve_passages(test["query"], top_k=3)

    if not results:
        print("No matching passages found.")
        continue

    for rank, result in enumerate(results, start=1):
        print(
            f"\n{rank}. {result['source']} | "
            f"Passage {result['passage_id']} | "
            f"Score: {result['score']}"
        )
        print(result["content"][:250].replace("\n", " "))
