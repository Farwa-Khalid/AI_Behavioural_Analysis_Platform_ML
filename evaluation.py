
import json
import pandas as pd

from transformers import pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
    hamming_loss,
    classification_report
)

from shared_utils.enrichment import generate_enriched_text
from shared_utils.compact_enrichment import generate_compact_enriched_text


# ==========================================
# CONFIGURATION
# ==========================================

DATASET_PATH = "evaluation_dataset.jsonl"
THRESHOLD = 0.50

SCORE_OUTPUT = "evaluation_scores.csv"
METRICS_OUTPUT = "evaluation_metrics.csv"
LABEL_OUTPUT = "evaluation_per_label.csv"


# ==========================================
# LOAD DATASET
# ==========================================

def load_dataset():

    records = []

    with open(DATASET_PATH, "r", encoding="utf-8-sig") as file:

        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            record = json.loads(line)

            required_fields = [
                "id", "text", "gold_labels", "split", "category"
            ]

            for field in required_fields:
                if field not in record:
                    raise ValueError(
                        f"Missing field '{field}' at line {line_number}"
                    )

            records.append(record)

    if not records:
        raise ValueError("Dataset is empty.")

    ids = [record["id"] for record in records]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate IDs found in dataset.")

    return records


# ==========================================
# LOAD PRETRAINED MODEL ONCE
# ==========================================

print("\nLoading GoEmotions model...")

classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)

print("Model loaded successfully.")


# ==========================================
# GET ALL 28 EMOTION SCORES
# ==========================================

def classify_all_labels(text):

    output = classifier(text)

    # Handle nested pipeline output
    if output and isinstance(output[0], list):
        output = output[0]

    score_map = {
        item["label"]: float(item["score"])
        for item in output
    }

    if len(score_map) != 28:
        raise ValueError(
            f"Expected 28 labels, received {len(score_map)}"
        )

    return score_map


# ==========================================
# CREATE E1, E2 AND E3 INPUTS
# ==========================================

def generate_experiment_inputs(text):

    # E1: Original text
    e1 = text

    # E2: Detailed enrichment
    e2_result = generate_enriched_text(text)
    e2 = e2_result["enriched_text"]

    # E3: Compact enrichment
    e3_result = generate_compact_enriched_text(text)
    e3 = e3_result["compact_enriched_text"]

    return {
        "E1_original": e1,
        "E2_detailed": e2,
        "E3_compact": e3
    }


# ==========================================
# RUN ALL EXPERIMENTS
# ==========================================

def run_experiments(records):

    score_rows = []

    labels = None

    total = len(records)

    for index, record in enumerate(records, start=1):

        print(
            f"\nProcessing {index}/{total}: {record['id']}"
        )

        inputs = generate_experiment_inputs(record["text"])

        for approach, input_text in inputs.items():

            scores = classify_all_labels(input_text)

            # Establish a consistent label order
            if labels is None:
                labels = sorted(scores.keys())

            if set(scores.keys()) != set(labels):
                raise ValueError("Emotion label mismatch.")

            row = {
                "id": record["id"],
                "split": record["split"],
                "category": record["category"],
                "approach": approach,
                "text": record["text"],
                "input_text": input_text,
                "gold_labels": json.dumps(record["gold_labels"])
            }

            for label in labels:
                row[f"score_{label}"] = scores[label]

            row["predicted_labels"] = json.dumps([
                label
                for label in labels
                if scores[label] >= THRESHOLD
            ])

            score_rows.append(row)

    return score_rows, labels


# ==========================================
# CALCULATE METRICS
# ==========================================

def calculate_metrics(score_rows, labels):

    df = pd.DataFrame(score_rows)

    mlb = MultiLabelBinarizer(classes=labels)
    mlb.fit([labels])

    summary_rows = []
    per_label_rows = []

    for split in ["validation", "test"]:

        split_df = df[df["split"] == split]

        if split_df.empty:
            continue

        for approach in [
            "E1_original",
            "E2_detailed",
            "E3_compact"
        ]:

            approach_df = split_df[
                split_df["approach"] == approach
            ]

            y_true_labels = [
                json.loads(value)
                for value in approach_df["gold_labels"]
            ]

            y_pred_labels = [
                json.loads(value)
                for value in approach_df["predicted_labels"]
            ]

            # Check that every reference label exists
            for example_labels in y_true_labels:
                unknown = set(example_labels) - set(labels)

                if unknown:
                    raise ValueError(
                        f"Unknown gold labels: {unknown}"
                    )

            y_true = mlb.transform(y_true_labels)
            y_pred = mlb.transform(y_pred_labels)

            macro_p, macro_r, macro_f1, _ = (
                precision_recall_fscore_support(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0
                )
            )

            micro_p, micro_r, micro_f1, _ = (
                precision_recall_fscore_support(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0
                )
            )

            exact_match = accuracy_score(y_true, y_pred)

            hamming = hamming_loss(y_true, y_pred)

            summary_rows.append({
                "split": split,
                "approach": approach,
                "threshold": THRESHOLD,
                "examples": len(approach_df),
                "macro_precision": macro_p,
                "macro_recall": macro_r,
                "macro_f1": macro_f1,
                "micro_precision": micro_p,
                "micro_recall": micro_r,
                "micro_f1": micro_f1,
                "exact_match_accuracy": exact_match,
                "hamming_loss": hamming
            })

            # Individual emotion metrics
            report = classification_report(
                y_true,
                y_pred,
                target_names=labels,
                output_dict=True,
                zero_division=0
            )

            for label in labels:

                per_label_rows.append({
                    "split": split,
                    "approach": approach,
                    "emotion": label,
                    "precision": report[label]["precision"],
                    "recall": report[label]["recall"],
                    "f1_score": report[label]["f1-score"],
                    "support": report[label]["support"]
                })

    return summary_rows, per_label_rows


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():

    print("\nLoading evaluation dataset...")

    records = load_dataset()

    print("Total examples:", len(records))
    print(
        "Validation examples:",
        sum(r["split"] == "validation" for r in records)
    )
    print(
        "Test examples:",
        sum(r["split"] == "test" for r in records)
    )

    print("\nRunning E1, E2 and E3...")

    score_rows, labels = run_experiments(records)

    print("\nDetected emotion labels:", len(labels))

    summary_rows, per_label_rows = calculate_metrics(
        score_rows,
        labels
    )

    # Save complete results
    pd.DataFrame(score_rows).to_csv(
        SCORE_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(summary_rows).to_csv(
        METRICS_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(per_label_rows).to_csv(
        LABEL_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== EVALUATION COMPLETE ==========")

    print("\nSUMMARY METRICS:")

    print(
        pd.DataFrame(summary_rows).round(4).to_string(index=False)
    )

    print("\nGenerated files:")
    print(SCORE_OUTPUT)
    print(METRICS_OUTPUT)
    print(LABEL_OUTPUT)

    print("\nThreshold used:", THRESHOLD)


if __name__ == "__main__":
    main()
