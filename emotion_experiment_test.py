
from emotion_module.emotion_model import detect_emotions


print("\n========== EMOTION EXPERIMENT COMPARISON ==========")

text = input("\nEnter text: ")

try:

    result = detect_emotions(text)

    print("\nOriginal Text:")
    print(result["original_text"])

    experiments = result["experiments"]

    for experiment_name, experiment in experiments.items():

        print("\n" + "=" * 55)
        print(experiment_name)
        print("=" * 55)

        print("\nInput sent to model:")
        print(experiment["input_text"])

        print("\nTop 3 emotion predictions:")

        for prediction in experiment["predictions"]:

            print(
                f"{prediction['label']}: "
                f"{prediction['score']}"
            )

        if "context_phrases" in experiment:

            print("\nCompact context phrases:")
            print(experiment["context_phrases"])

except (TypeError, ValueError) as error:

    print("\nInput Error:", error)
