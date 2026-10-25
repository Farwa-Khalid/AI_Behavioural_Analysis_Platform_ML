from transformers import pipeline

import shap
import spacy
from transformers import pipeline


from collections import Counter

classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def detect_sentiment(text):

    result = classifier(text)[0]

    return {
        "module": "sentiment",

        "predictions": [
            {
                "label": result["label"],
                "score": round(result["score"], 4)
            }
        ]
    }


_nlp = None
_explainer = None

# Words that look like aspects but carry no useful meaning
STOP_ASPECTS = {"thing", "lot", "bit", "way", "kind", "sort"}
MODIFIER_DEPS = {"advmod", "neg", "amod"}


# ---------- loaders (run once, reused afterwards) ----------

def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_explainer():
    """SHAP needs scores for ALL classes, so build a second pipeline that
    reuses your already-loaded model (no extra memory)."""
    global _explainer
    if _explainer is None:
        shap_pipe = pipeline(
            "sentiment-analysis",
            model=classifier.model,
            tokenizer=classifier.tokenizer,
            top_k=None,
        )
        _explainer = shap.Explainer(shap_pipe)
    return _explainer


# ---------- Step 1: SHAP values aligned to spaCy words ----------

def _word_attributions(text, doc):
    """Return one SHAP score per spaCy token (toward POSITIVE class).
    Positive = pushes toward POSITIVE, negative = pushes toward NEGATIVE."""
    sv = _get_explainer()([text], max_evals=200, batch_size=32)
    pos_idx = list(sv.output_names).index("POSITIVE")
    values = sv.values[0][:, pos_idx]
    segments = sv.data[0]

    # char position -> spaCy token index
    char2tok = {}
    for tok in doc:
        for c in range(tok.idx, tok.idx + len(tok)):
            char2tok[c] = tok.i

    scores = [0.0] * len(doc)
    lowered = text.lower()
    cursor = 0
    for seg, val in zip(segments, values):
        piece = seg.strip().lower()
        if not piece:
            continue
        start = lowered.find(piece, cursor)
        if start == -1:
            continue
        end = start + len(piece)
        cursor = end
        hit = sorted({char2tok[c] for c in range(start, end) if c in char2tok})
        for i in hit:  # split value if a SHAP piece spans several spaCy tokens
            scores[i] += float(val) / len(hit)

    return scores, float(sv.base_values[0][pos_idx])


# ---------- Step 2 & 3: aspects and their opinion words ----------

def _with_modifiers(tok):
    """'slow' -> ['slow', 'terribly']"""
    return [tok] + [c for c in tok.children if c.dep_ in MODIFIER_DEPS]


def _opinion_tokens(noun):
    found = []

    # "great food", "very slow service"
    for child in noun.children:
        if child.dep_ == "amod":
            found += _with_modifiers(child)

    # "service was terribly slow", "food and service were great"
    subj = noun
    while subj.dep_ == "conj" and subj.head.pos_ in {"NOUN", "PROPN"}:
        subj = subj.head
    if subj.dep_ in {"nsubj", "nsubjpass"}:
        head = subj.head
        if head.pos_ in {"ADJ", "VERB"}:
            found += _with_modifiers(head)
        for child in head.children:
            if child.dep_ in {"acomp", "attr", "oprd", "neg", "advmod"}:
                found += _with_modifiers(child)
    # "we enjoyed the food", "disappointed by the poor service"
    if noun.dep_ in {"dobj", "obj"} and noun.head.pos_ in {"ADJ", "VERB"}:
        found += _with_modifiers(noun.head)

    # "efficient with their service", "happy with the food"
    if noun.dep_ == "pobj" and noun.head.dep_ == "prep":
        gov = noun.head.head
        if gov.pos_ in {"ADJ", "VERB"}:
            found += _with_modifiers(gov)
    return found


def _polarity(score, thr):
    if score > thr:
        return "positive"
    if score < -thr:
        return "negative"
    return "neutral"


# ---------- Step 4 & 5: main function ----------

def explain_sentiment(text, neutral_threshold=0.03):
    doc = _get_nlp()(text)
    scores, base_value = _word_attributions(text, doc)

    # collect candidate aspects
    candidates, usage = [], Counter()
    for tok in doc:
        if (tok.pos_ not in {"NOUN", "PROPN"}
                or tok.dep_ == "compound"
                or tok.lemma_.lower() in STOP_ASPECTS):
            continue
        compounds = [c for c in tok.lefts if c.dep_ == "compound"]
        opinion = {t.i: t for t in _opinion_tokens(tok)}
        if not opinion:          # no opinion about this noun -> not an aspect
            continue
        name = " ".join([c.text for c in compounds] + [tok.text]).lower()
        own = [c.i for c in compounds] + [tok.i]
        candidates.append((name, own, opinion))
        usage.update(opinion.keys())

    # aggregate; an opinion word shared by 2 aspects is split between them
    merged, used_idx = {}, set()
    for name, own, opinion in candidates:
        score = sum(scores[i] for i in own)
        score += sum(scores[i] / usage[i] for i in opinion)
        used_idx.update(own)
        used_idx.update(opinion.keys())
        entry = merged.setdefault(name, {"score": 0.0, "evidence": []})
        entry["score"] += score
        entry["evidence"] += [opinion[i].text for i in sorted(opinion)]

    aspects = [
        {
            "aspect": name,
            "score": round(e["score"], 4),
            "polarity": _polarity(e["score"], neutral_threshold),
            "evidence": e["evidence"],
        }
        for name, e in merged.items()
    ]

    # how much of the model's total evidence the aspects account for
    total = sum(abs(s) for s in scores)
    coverage = (sum(abs(scores[i]) for i in used_idx) / total) if total else 0.0

    # overall label + summary
    overall = detect_sentiment(text)["predictions"][0]["label"]
    pos = [a for a in aspects if a["polarity"] == "positive"]
    neg = [a for a in aspects if a["polarity"] == "negative"]
    is_mixed = bool(pos) and bool(neg)

    if not aspects:
        summary = f"Overall {overall}. No aspect-level opinions were found."
    else:
        driver = max(aspects, key=lambda a: abs(a["score"]))
        if is_mixed:
            summary = (
                f"Mixed sentiment: {', '.join(a['aspect'] for a in pos)} positive, "
                f"{', '.join(a['aspect'] for a in neg)} negative. "
                f"Overall {overall} because '{driver['aspect']}' had the "
                f"strongest influence ({driver['score']:+.2f})."
            )
        else:
            summary = (
                f"Overall {overall}. All aspect evidence points the same way; "
                f"strongest aspect: '{driver['aspect']}' ({driver['score']:+.2f})."
            )

    return {
        "module": "sentiment",
        "method": "SHAP + dependency-based aspect aggregation",
        "overall_label": overall,
        "is_mixed": is_mixed,
        "aspects": aspects,
        "aspect_coverage": round(coverage, 3),
        "base_value_positive": round(base_value, 4),
        "summary": summary,
    }