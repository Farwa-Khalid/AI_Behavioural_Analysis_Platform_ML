
from knowledge_retriever import load_documents

documents = load_documents()

print("Total documents:", len(documents))
print("=" * 60)

for document in documents:
    print("\nSource:", document["source"])

    sections = [
        section.strip()
        for section in document["content"].split("\n## ")
        if section.strip()
    ]

    print("Sections found:", len(sections))

    for section in sections[:3]:
        print("\nSection preview:")
        print(section[:200].replace("\n", " "))

