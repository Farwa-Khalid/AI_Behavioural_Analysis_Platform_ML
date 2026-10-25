"""Statistical check + error analysis for eval_results.json (no SHAP needed, runs in seconds)."""
import json
import sys
import random
from collections import defaultdict

d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "eval_results.json", encoding="utf-8"))["details"]
methods = ["sentence_label", "own_shap", "window_shap", "ours_linked", "ours_fallback"]

# group by sentence: aspects in one sentence are not independent, so resample sentences
by_sentence = defaultdict(list)
for r in d:
    by_sentence[r["sentence"]].append(r)
sentences = list(by_sentence.values())
random.seed(0)


def acc(rows, m):
    return sum(r[m] == r["gold"] for r in rows) / len(rows) if rows else float("nan")


def bootstrap(fn, n=2000):
    vals = []
    for _ in range(n):
        sample = [r for s in random.choices(sentences, k=len(sentences)) for r in s]
        vals.append(fn(sample))
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.975 * n)]


print(f"{len(d)} aspects in {len(sentences)} sentences\n")

print("Accuracy with 95% bootstrap CI")
for m in methods:
    lo, hi = bootstrap(lambda rows: acc(rows, m))
    print(f"  {m:<16}{acc(d, m):.3f}   [{lo:.3f}, {hi:.3f}]")

print("\nPaired differences (95% CI; if it contains 0, the difference is not significant)")
for a, b in [("ours_fallback", "window_shap"), ("ours_linked", "window_shap"),
             ("ours_fallback", "sentence_label"), ("window_shap", "sentence_label")]:
    lo, hi = bootstrap(lambda rows: acc(rows, a) - acc(rows, b))
    print(f"  {a} - {b}: {acc(d, a) - acc(d, b):+.3f}   [{lo:+.3f}, {hi:+.3f}]")

linked = [r for r in d if r["opinion_words"]]
unlinked = [r for r in d if not r["opinion_words"]]
print(f"\nWhere linking fires (n={len(linked)}) vs not (n={len(unlinked)})")
for name, rows in [("linked", linked), ("not linked", unlinked)]:
    print(f"  {name:<11}", {m: round(acc(rows, m), 3) for m in methods})

print("\nLinking helped (ours_linked right, window_shap wrong):")
for r in [r for r in d if r["ours_linked"] == r["gold"] != r["window_shap"]][:10]:
    print(f"  {r['term']} | {r['opinion_words']} | {r['sentence']}")

print("\nLinking hurt (ours_linked wrong, window_shap right):")
for r in [r for r in d if r["window_shap"] == r["gold"] != r["ours_linked"]][:10]:
    print(f"  {r['term']} | {r['opinion_words']} | gold={r['gold']} | {r['sentence']}")