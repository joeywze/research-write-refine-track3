"""
Stylometric "AI-smell" detector for academic prose.

Why stylometric features instead of a black-box classifier:
  * Every point of the score traces back to a sentence the reviser can fix,
    which is what the rewriting loop needs (a bare probability gives the
    reviser nothing to act on).
  * We have ~1.8k real EMNLP abstracts but only a few hundred LLM paragraphs,
    which is too little to train a deep classifier without it memorising topic.
  * Each feature maps onto one symptom in the track brief, so the score is
    explainable in the report.

The score is calibrated against real EMNLP 2025 abstracts: each feature is
expressed as how unusual it is relative to that human reference distribution,
and a logistic regression (fit in train_detector.py) weights the features.
Score = P(AI) * 100.

Usage:
    python src/detector.py "some text"          # score a string
    python src/detector.py --file draft.md      # score a file
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = PROJECT_ROOT / "results" / "detection" / "detector_model.json"

# ------------------------------------------------------------------
# Lexicons. Kept short and specific on purpose: a long list of "AI words"
# mostly catches ordinary academic vocabulary.
# ------------------------------------------------------------------

HEDGES = [
    "may", "might", "could", "potentially", "possibly", "perhaps", "likely",
    "arguably", "somewhat", "relatively", "generally", "typically", "often",
    "tend to", "tends to", "appears to", "appear to", "seems to", "seem to",
    "suggests", "suggest", "can be",
]

AI_VOCAB = [
    "delve", "delves", "landscape", "crucial", "pivotal", "robust",
    "seamless", "seamlessly", "comprehensive", "notably", "underscore",
    "underscores", "underscoring", "highlight", "highlights", "highlighting",
    "leverage", "leverages", "leveraging", "multifaceted", "nuanced",
    "intricate", "realm", "tapestry", "holistic", "paradigm", "transformative",
    "groundbreaking", "cutting-edge", "unprecedented", "foster", "fosters",
    "fostering", "facilitate", "facilitates", "enhance", "enhances",
    "enhancing", "valuable", "insights", "interplay", "principled",
    "systematically", "inherently", "broader", "meaningful", "remains",
    "promising", "essential", "ensure", "ensures", "ensuring",
]

AI_PHRASES = [
    "it is important to note", "it is worth noting", "plays a crucial role",
    "plays a key role", "plays an important role", "in today's",
    "rapidly evolving", "paving the way", "pave the way", "shed light",
    "sheds light", "a wide range of", "a growing body", "in the context of",
    "not only", "rather than", "these results highlight", "these findings",
    "this work", "taken together", "in summary", "overall,",
    "more broadly", "in particular,", "by doing so", "a step toward",
    "a promising direction", "remains an open", "remains challenging",
    "has emerged as", "have emerged as", "serves as", "aims to",
]

PROMO_ADJ = [
    "groundbreaking", "transformative", "revolutionary", "remarkable",
    "unprecedented", "state-of-the-art", "novel", "powerful", "innovative",
    "significant", "substantial", "superior", "compelling", "effective",
    "efficient", "scalable", "robust", "rich", "diverse", "strong",
]

TRANSITIONS = [
    "furthermore", "moreover", "additionally", "in addition", "importantly",
    "notably", "consequently", "thus", "therefore", "overall", "finally",
    "specifically", "in particular", "as a result", "to this end",
    "in contrast", "similarly", "however", "instead", "together",
]

_ABBREV = re.compile(
    r"\b(e\.g|i\.e|et al|etc|vs|Fig|Figs|Tab|Eq|Sec|cf|approx|resp|No)\.",
    re.IGNORECASE,
)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])")
_WORD = re.compile(r"[A-Za-z][A-Za-z\-']*")
# "X, Y, and Z" / "X, Y and Z" where each slot is 1-3 words
_TRIPLET = re.compile(
    r"\b[\w\-]+(?: [\w\-]+){0,2}, [\w\-]+(?: [\w\-]+){0,2},? (?:and|or) [\w\-]+",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """Strip markdown the generator emits (headings, bold, bullets)."""
    lines = []
    for line in str(text).splitlines():
        s = line.strip()
        if re.match(r"^#{1,6}\s", s):
            continue
        s = re.sub(r"^[-*•]\s+", "", s)
        s = re.sub(r"^\d+[.)]\s+", "", s)
        lines.append(s)
    text = "\n".join(lines)
    text = re.sub(r"\*\*|__|\*|`", "", text)
    return text.strip()


def split_paragraphs(text: str, min_words: int = 40) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", clean_text(text))]
    paras = [re.sub(r"\s*\n\s*", " ", p) for p in paras]
    return [p for p in paras if len(p.split()) >= min_words]


def split_sentences(text: str) -> list[str]:
    protected = _ABBREV.sub(lambda m: m.group(0).replace(".", "<DOT>"), text)
    protected = re.sub(r"\s+", " ", protected).strip()
    sents = _SENT_SPLIT.split(protected)
    sents = [s.replace("<DOT>", ".").strip() for s in sents]
    return [s for s in sents if len(_WORD.findall(s)) >= 2]


def _count_terms(lower: str, terms: list[str]) -> int:
    n = 0
    for t in terms:
        n += len(re.findall(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", lower))
    return n


@dataclass
class Analysis:
    features: dict[str, float]
    flagged: list[dict] = field(default_factory=list)  # per-sentence reasons
    n_words: int = 0
    n_sents: int = 0


FEATURE_NAMES = [
    "sent_len_cv",        # burstiness: std/mean sentence length (low = AI)
    "short_sent_rate",    # share of sentences under 12 words (low = AI)
    "long_sent_rate",     # share over 35 words
    "hedge_per_100w",
    "stacked_hedge_rate", # sentences with 2+ hedges
    "ai_vocab_per_100w",
    "ai_phrase_per_100w",
    "promo_adj_per_100w",
    "transition_open_rate",  # sentences opening with a connective
    "triplet_rate",       # sentences containing "X, Y, and Z"
    "emdash_per_100w",
    "colon_per_sent",
    "we_rate",            # first person plural per sentence (human papers use "we")
    "digit_per_100w",     # concrete numbers (humans report them)
    "paren_per_100w",     # parentheticals, citations, acronyms
    "ttr",                # moving-average type-token ratio (window 40)
    "trigram_repeat",     # repeated word trigrams
    "mean_word_len",
]


def analyse(text: str) -> Analysis:
    text = clean_text(text)
    flat = re.sub(r"\s+", " ", text)
    lower = flat.lower()
    words = _WORD.findall(flat)
    nw = max(len(words), 1)
    sents = split_sentences(flat)
    ns = max(len(sents), 1)
    lens = [len(_WORD.findall(s)) for s in sents] or [nw]
    mean_len = sum(lens) / len(lens)
    sd = math.sqrt(sum((x - mean_len) ** 2 for x in lens) / len(lens))

    flagged = []
    hedge_sents = trans_open = triplet_sents = 0
    for i, s in enumerate(sents):
        sl = s.lower()
        reasons = []
        h = _count_terms(sl, HEDGES)
        if h >= 2:
            hedge_sents += 1
            reasons.append(f"{h} hedges")
        first = re.sub(r"^[\"'(\[]+", "", sl)
        for t in TRANSITIONS:
            if first.startswith(t + ",") or first.startswith(t + " "):
                trans_open += 1
                reasons.append(f"opens with '{t}'")
                break
        if _TRIPLET.search(s):
            triplet_sents += 1
            reasons.append("list of three")
        hits = [t for t in AI_VOCAB + AI_PHRASES if re.search(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", sl)]
        if hits:
            reasons.append("stock wording: " + ", ".join(hits[:4]))
        promo = [t for t in PROMO_ADJ if re.search(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", sl)]
        if len(promo) >= 2:
            reasons.append("promotional: " + ", ".join(promo[:3]))
        if "—" in s:
            reasons.append("em-dash")
        if reasons:
            flagged.append({"index": i, "sentence": s, "reasons": reasons})

    toks = [w.lower() for w in words]
    # moving-average type-token ratio (window 40): robust to text length
    win = 40
    if len(toks) <= win:
        ttr = len(set(toks)) / max(len(toks), 1)
    else:
        ttr = sum(len(set(toks[i:i + win])) for i in range(len(toks) - win + 1)) / (win * (len(toks) - win + 1))
    tri = Counter(zip(toks, toks[1:], toks[2:]))
    rep = sum(c - 1 for c in tri.values() if c > 1) / max(len(toks) - 2, 1)

    f = {
        "sent_len_cv": sd / mean_len if mean_len else 0.0,
        "short_sent_rate": sum(1 for x in lens if x < 12) / len(lens),
        "long_sent_rate": sum(1 for x in lens if x > 35) / len(lens),
        "hedge_per_100w": 100 * _count_terms(lower, HEDGES) / nw,
        "stacked_hedge_rate": hedge_sents / ns,
        "ai_vocab_per_100w": 100 * _count_terms(lower, AI_VOCAB) / nw,
        "ai_phrase_per_100w": 100 * _count_terms(lower, AI_PHRASES) / nw,
        "promo_adj_per_100w": 100 * _count_terms(lower, PROMO_ADJ) / nw,
        "transition_open_rate": trans_open / ns,
        "triplet_rate": triplet_sents / ns,
        "emdash_per_100w": 100 * flat.count("—") / nw,
        "colon_per_sent": flat.count(":") / ns,
        "we_rate": len(re.findall(r"\b(we|our|us)\b", lower)) / ns,
        "digit_per_100w": 100 * len(re.findall(r"\d+(?:\.\d+)?", flat)) / nw,
        "paren_per_100w": 100 * flat.count("(") / nw,
        "ttr": ttr,
        "trigram_repeat": rep,
        "mean_word_len": sum(len(w) for w in words) / nw,
    }
    return Analysis(features=f, flagged=flagged, n_words=len(words), n_sents=len(sents))


# ------------------------------------------------------------------
# Scoring with the trained weights
# ------------------------------------------------------------------

_MODEL_CACHE: dict | None = None


def load_model(path: Path = MODEL_FILE) -> dict:
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found. Run `python src/train_detector.py` first."
            )
        _MODEL_CACHE = json.loads(path.read_text())
    return _MODEL_CACHE


def score(text: str, model: dict | None = None) -> dict:
    """Return {'score': 0-100, 'features', 'contributions', 'flagged'}."""
    model = model or load_model()
    a = analyse(text)
    z = {}
    contrib = {}
    logit = model["intercept"]
    for name in model["features"]:
        mu, sd = model["mean"][name], model["std"][name]
        zv = (a.features[name] - mu) / sd if sd else 0.0
        zv = max(min(zv, 6.0), -6.0)
        z[name] = zv
        c = model["coef"][name] * zv
        contrib[name] = c
        logit += c
    p = 1 / (1 + math.exp(-logit))
    return {
        "score": round(100 * p, 1),
        "features": a.features,
        "z": z,
        "contributions": dict(sorted(contrib.items(), key=lambda kv: -kv[1])),
        "flagged": a.flagged,
        "n_words": a.n_words,
        "n_sents": a.n_sents,
    }


PLAIN_NAMES = {
    "sent_len_cv": "sentence lengths are too uniform",
    "short_sent_rate": "almost no short sentences",
    "long_sent_rate": "share of very long sentences",
    "hedge_per_100w": "hedge density",
    "stacked_hedge_rate": "sentences with stacked hedges",
    "ai_vocab_per_100w": "stock 'LLM' vocabulary",
    "ai_phrase_per_100w": "stock phrases",
    "promo_adj_per_100w": "promotional adjectives",
    "transition_open_rate": "sentences opening with a connective",
    "triplet_rate": "lists of three",
    "emdash_per_100w": "em-dashes",
    "colon_per_sent": "colons",
    "we_rate": "first-person 'we'",
    "digit_per_100w": "concrete numbers",
    "paren_per_100w": "parentheticals / acronyms / citations",
    "ttr": "vocabulary variety",
    "trigram_repeat": "repeated phrases",
    "mean_word_len": "word length",
}


def explain(result: dict, top: int = 4) -> list[str]:
    """Human-readable list of the features pushing the score up."""
    out = []
    for name, c in list(result["contributions"].items())[:top]:
        if c <= 0.15:
            break
        out.append(f"{PLAIN_NAMES.get(name, name)} (z={result['z'][name]:+.1f}, +{c:.2f} logit)")
    return out


def _cli():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = Path(args.file).read_text() if args.file else (args.text or sys.stdin.read())
    paras = split_paragraphs(text, min_words=40)
    if len(paras) > 1:
        # Calibrated on paragraphs (~100-200 words): score each, report the mean.
        scored = sorted(((score(p), p) for p in paras), key=lambda x: -x[0]["score"])
        mean = sum(r["score"] for r, _ in scored) / len(scored)
        if args.json:
            print(json.dumps({"mean_paragraph_score": mean,
                              "paragraphs": [{"score": r["score"], "text": p} for r, p in scored]}, indent=2))
            return
        print(f"\nMean AI-likeness over {len(paras)} paragraphs: {mean:.1f} / 100  (scored per paragraph)")
        print("\nMost AI-sounding paragraphs:")
        for r, p in scored[:5]:
            print(f"\n  [{r['score']:.0f}] {p[:150]}...")
            for line in explain(r, top=3):
                print("      -", line)
        return
    r = score(text)
    if args.json:
        print(json.dumps(r, indent=2))
        return
    print(f"\nAI-likeness score: {r['score']:.1f} / 100   ({r['n_words']} words, {r['n_sents']} sentences)")
    print("\nWhat is driving it:")
    for line in explain(r, top=6) or ["nothing stands out"]:
        print("  -", line)
    print("\nFlagged sentences:")
    for fl in r["flagged"][:10]:
        print(f"  [{fl['index']}] {'; '.join(fl['reasons'])}")
        print(f"      {fl['sentence'][:160]}")


if __name__ == "__main__":
    _cli()
