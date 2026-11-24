
from shared_utils.context_processor import interpret_context


def main():

    print("\n========== CONTEXT-AWARE INTERPRETATION ==========\n")

    text = input("Enter text: ")

    try:

        result = interpret_context(text)

        print("\nOriginal Text:")
        print(result["original_text"])

        print("\nSlang Interpretations:")

        for item in result["slang_interpretations"]:

            print("\nTerm:", item["term"])

            print(
                "Possible meanings:",
                item["possible_meanings"]
            )

            print(
                "Selected interpretation:",
                item["selected_interpretation"]
            )

            print("Reason:", item["context_reason"])

            print("Status:", item["status"])

        print("\nEmoji Interpretations:")

        for item in result["emoji_interpretations"]:

            print("\nEmoji:", item["emoji"])

            print(
                "Possible meanings:",
                item["possible_meanings"]
            )

            print(
                "Selected interpretation:",
                item["selected_interpretation"]
            )

            print("Reason:", item["context_reason"])

            print("Status:", item["status"])

    except (ValueError, TypeError) as error:

        print("Input Error:", error)


if __name__ == "__main__":
    main()
