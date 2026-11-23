
import json
import re
from pathlib import Path

from shared_utils.preprocessing import preprocess_text


# Load contextual rules from JSON
RULES_FILE = (
    Path(__file__).parent / "mappings" / "context_rules.json"
)


def load_context_rules():

    with open(RULES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    required_sections = [
        "slang_terms",
        "slang_groups",
        "emoji_terms",
        "emoji_groups"
    ]

    for section in required_sections:
        if section not in data or not isinstance(data[section], dict):
            raise ValueError(f"Invalid or missing section: {section}")

    return data


CONTEXT_RULES = load_context_rules()


# Check whether a keyword or phrase exists in the text
def find_context_keywords(text, keywords):

    text = text.lower()
    found = []

    for keyword in keywords:

        pattern = (
            rf"(?<!\w){re.escape(keyword.lower())}(?!\w)"
        )

        if re.search(pattern, text):
            found.append(keyword)

    return found


# Select an interpretation based on contextual evidence
def evaluate_context(text, group_config):

    # Handle expressions with a default interpretation
    if "default" in group_config:

        return {
            "possible_meanings": [group_config["default"]],
            "selected_interpretation": group_config["default"],
            "context_reason": group_config["reason"],
            "matched_keywords": [],
            "status": "interpreted"
        }

    rules = group_config.get("rules", [])

    possible_meanings = [
        rule["meaning"] for rule in rules
    ]

    scored_rules = []

    for rule in rules:

        matched = find_context_keywords(
            text,
            rule["keywords"]
        )

        scored_rules.append({
            "meaning": rule["meaning"],
            "reason": rule["reason"],
            "matched_keywords": matched,
            "score": len(matched)
        })

    # Keep only rules with contextual evidence
    matched_rules = [
        rule for rule in scored_rules
        if rule["score"] > 0
    ]

    # No contextual evidence
    if not matched_rules:

        return {
            "possible_meanings": possible_meanings,
            "selected_interpretation": None,
            "context_reason": None,
            "matched_keywords": [],
            "status": "ambiguous"
        }

    # Find the highest contextual score
    highest_score = max(
        rule["score"] for rule in matched_rules
    )

    best_rules = [
        rule for rule in matched_rules
        if rule["score"] == highest_score
    ]

    # If multiple meanings have equal scores,
    # preserve ambiguity instead of guessing
    if len(best_rules) > 1:

        matched_keywords = sorted({
            keyword
            for rule in best_rules
            for keyword in rule["matched_keywords"]
        })

        return {
            "possible_meanings": possible_meanings,
            "selected_interpretation": None,
            "context_reason": "Multiple interpretations have equal contextual evidence",
            "matched_keywords": matched_keywords,
            "status": "ambiguous"
        }

    selected = best_rules[0]

    return {
        "possible_meanings": possible_meanings,
        "selected_interpretation": selected["meaning"],
        "context_reason": selected["reason"],
        "matched_keywords": selected["matched_keywords"],
        "status": "interpreted"
    }


# Interpret slang dynamically using JSON rules
def interpret_slang_context(text, slang_matches):

    interpretations = []

    for item in slang_matches:

        term = item["normalized_term"]

        group_name = CONTEXT_RULES["slang_terms"].get(term)

        if group_name is None:

            result = {
                "possible_meanings": item["possible_meanings"],
                "selected_interpretation": None,
                "context_reason": None,
                "matched_keywords": [],
                "status": "ambiguous"
            }

        else:

            group_config = CONTEXT_RULES["slang_groups"].get(
                group_name
            )

            if group_config is None:
                raise ValueError(
                    f"Missing slang group: {group_name}"
                )

            result = evaluate_context(
                text,
                group_config
            )

        interpretations.append({
            "term": item["term"],
            **result
        })

    return interpretations


# Interpret emojis dynamically using JSON rules
def interpret_emoji_context(text, emoji_matches):

    interpretations = []

    for item in emoji_matches:

        emoji_character = item["emoji"]

        group_name = CONTEXT_RULES["emoji_terms"].get(
            emoji_character
        )

        if group_name is None:

            result = {
                "possible_meanings": item["genz_interpretations"],
                "selected_interpretation": None,
                "context_reason": None,
                "matched_keywords": [],
                "status": "ambiguous"
            }

        else:

            group_config = CONTEXT_RULES["emoji_groups"].get(
                group_name
            )

            if group_config is None:
                raise ValueError(
                    f"Missing emoji group: {group_name}"
                )

            result = evaluate_context(
                text,
                group_config
            )

        interpretations.append({
            "emoji": emoji_character,
            **result
        })

    return interpretations


# Main contextual interpretation function
def interpret_context(text):

    preprocessing_result = preprocess_text(text)

    slang_results = interpret_slang_context(
        text,
        preprocessing_result["slang_matches"]
    )

    emoji_results = interpret_emoji_context(
        text,
        preprocessing_result["emoji_matches"]
    )

    return {
        "original_text": text,
        "slang_interpretations": slang_results,
        "emoji_interpretations": emoji_results
    }
