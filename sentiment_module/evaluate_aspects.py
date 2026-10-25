"""
Evaluate aspect-level SHAP explanations on SemEval-2014 Task 4 (Restaurants).

Task: given a sentence and a GOLD aspect term, predict its polarity
(positive / negative) using only the pretrained SST-2 model + SHAP.

Methods compared
  1. sentence_label  : every aspect gets the sentence-level label (no explainability)
  2. own_shap        : SHAP value of the aspect word itself (naive baseline)
  3. window_shap     : sum of SHAP values within +/-3 tokens of the aspect
  4. ours_linked     : own + SHAP of dependency-linked opinion words (your method)
  5. ours_fallback   : ours_linked, falling back to window_shap if no opinion word found

Run (from the sentiment_module folder):
  python evaluate_aspects.py --data Restaurants_Test_Gold.xml --limit 200
"""
import argparse
import json
import os
import xml.etree.ElementTree as ET
from collections import Counter

from sklearn.metrics import accuracy_score, f1_score

from sentiment_model import _get_nlp, _word_attributions, _opinion_tokens
from sentiment_model import detect_sentiment

LABELS = ["positive", "negative"]
WINDOW = 3


def load_semeval(path):
    """Keep only positive/negative aspect terms (SST-2 model is binary)."""
    rows = []
    for s in ET.parse(path).getroot().iter("sentence"):
        text = s.find("text").text
        terms = []
        for t in s.iter("aspectTerm"):
            if t.get("polarity") in LABELS:
                terms.append({
                    "term": t.get("term"),
                    "from": int(t.get("from")),
                    "to": int(t.get("to")),
                    "polarity": t.get("polarity"),
                })
        if terms:
            rows.append({"text": text, "terms": terms})
    return rows


def span_tokens(doc, start, end):
    return [t for t in doc if t.idx < end and t.idx + len(t) > start]


def span_head(span):
    ids = {t.i for t in span}
    for t in span:
        if t.head.i not in ids or t.head.i == t.i:
            return t
    return span[-1]


def to_label(score):
    return "positive" if score > 0 else "negative"


def load_cache(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="SemEval-2014 Restaurants XML file")
    ap.add_argument("--limit", type=int, default=0, help="max sentences (0 = all)")
    ap.add_argument("--cache", default="shap_cache.json", help="SHAP cache so reruns are fast")
    ap.add_argument("--out", default="eval_results.json")
    ap.add_argument("--mixed_only", action="store_true")
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()

    nlp = _get_nlp()
    rows = load_semeval(args.data)
    if args.mixed_only:
        rows = [r for r in rows if len({t["polarity"] for t in r["terms"]}) > 1]
    if args.limit:
        rows = rows[args.offset: args.offset + args.limit]
    cache = load_cache(args.cache)
    

    methods = ["sentence_label", "own_shap", "window_shap", "ours_linked", "ours_fallback"]
    gold, preds, mixed_flags, details = [], {m: [] for m in methods}, [], []
    linked_found = 0

    for n, row in enumerate(rows, 1):
        text = row["text"]
        doc = nlp(text)

        if text not in cache:                      # SHAP is slow: compute once, reuse
            scores, _ = _word_attributions(text, doc)
            cache[text] = scores
            with open(args.cache, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        scores = cache[text]

        sent_label = detect_sentiment(text)["predictions"][0]["label"].lower()
        is_mixed = len({t["polarity"] for t in row["terms"]}) > 1

        # resolve each gold term to tokens + opinion tokens
        prepared = []
        for t in row["terms"]:
            span = span_tokens(doc, t["from"], t["to"])
            if not span:
                continue
            own_idx = {x.i for x in span}
            opinion = {x.i for x in _opinion_tokens(span_head(span))} - own_idx
            prepared.append((t, span, own_idx, opinion))

        usage = Counter()
        for _, _, _, opinion in prepared:
            usage.update(opinion)

        for t, span, own_idx, opinion in prepared:
            own = sum(scores[i] for i in own_idx)
            lo, hi = min(own_idx) - WINDOW, max(own_idx) + WINDOW
            window = sum(scores[i] for i in range(max(lo, 0), min(hi, len(doc) - 1) + 1))
            linked = own + sum(scores[i] / usage[i] for i in opinion)
            if opinion:
                linked_found += 1

            p = {
                "sentence_label": sent_label,
                "own_shap": to_label(own),
                "window_shap": to_label(window),
                "ours_linked": to_label(linked),
                "ours_fallback": to_label(linked if opinion else window),
            }
            gold.append(t["polarity"])
            mixed_flags.append(is_mixed)
            for m in methods:
                preds[m].append(p[m])
            details.append({"sentence": text, "term": t["term"], "gold": t["polarity"],
                            "opinion_words": [doc[i].text for i in sorted(opinion)], **p})

        if n % 20 == 0:
            print(f"processed {n}/{len(rows)} sentences")

    def report(idx, title):
        g = [gold[i] for i in idx]
        print(f"\n{title}  (n={len(g)} aspects)")
        print(f"{'method':<16}{'accuracy':>10}{'macro-F1':>10}")
        out = {}
        for m in methods:
            pr = [preds[m][i] for i in idx]
            acc = accuracy_score(g, pr)
            f1 = f1_score(g, pr, labels=LABELS, average="macro", zero_division=0)
            print(f"{m:<16}{acc:>10.3f}{f1:>10.3f}")
            out[m] = {"accuracy": round(acc, 4), "macro_f1": round(f1, 4)}
        return out

    all_idx = list(range(len(gold)))
    mixed_idx = [i for i in all_idx if mixed_flags[i]]
    results = {
        "all": report(all_idx, "ALL aspects"),
        "mixed_sentences": report(mixed_idx, "MIXED-polarity sentences only") if mixed_idx else {},
        "opinion_link_coverage": round(linked_found / max(len(gold), 1), 3),
    }
    print(f"\nAspects with a linked opinion word: {results['opinion_link_coverage']:.1%}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"results": results, "details": details}, f, indent=2)
    print(f"Saved {args.out} (use 'details' for error analysis)")


if __name__ == "__main__":
    main()
