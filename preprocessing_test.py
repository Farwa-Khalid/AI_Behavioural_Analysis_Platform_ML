
from shared_utils.preprocessing import preprocess_text


def main():

    print("\n========== LANGUAGE PROCESSING TEST ==========\n")

    text = input("Enter text: ")

    try:

        result = preprocess_text(text)

        print("\nOriginal Text:")
        print(result["original_text"])

        print("\nDetected Slang:")

        if result["slang_matches"]:

            for item in result["slang_matches"]:

                print(f"\nTerm: {item['term']}")
                print(f"Meanings: {item['possible_meanings']}")
                print(f"Position: {item['start']} - {item['end']}")

        else:
            print("No slang detected.")

        print("\nDetected Emojis:")

        if result["emoji_matches"]:

            for item in result["emoji_matches"]:

                print(f"\nEmoji: {item['emoji']}")
                print(f"Standard meaning: {item['standard_meaning']}")
                print(f"Gen Z meanings: {item['genz_interpretations']}")
                print(f"Position: {item['start']} - {item['end']}")

        else:
            print("No emojis detected.")

    except (ValueError, TypeError) as error:

        print("Input Error:", error)


if __name__ == "__main__":
    main()
