"""
Held-out check on real *body* text (not abstracts).

The detector is fit on human abstracts vs AI paragraphs from all sections, so
part of what it learns could be "abstract vs body section". This script tests
it on passages from the full PDFs of 18 real EMNLP 2025 papers (Cluster 7,
extracted on the research-idea branch) that it never saw during training,
against the AI body paragraphs (out-of-fold predictions).

Input : data/processed/cluster7_fulltext_evidence.csv (from research-idea branch)
Output: results/detection/heldout_fulltext.json, heldout_fulltext_passages.csv
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detector import score, split_sentences  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "cluster7_fulltext_evidence.csv"
OUT = ROOT / "results" / "detection"


def clean_window(w: str) -> str:
    w = re.sub(r"-\n(?=[a-z])", "", w)          # de-hyphenate line breaks
    keep = []
    for line in w.splitlines():
        s = line.strip()
        if not s or s.startswith(("Matched keyword", "=====", "Proceedings of", "November", "Correspondence")):
            continue
        if "@" in s or re.fullmatch(r"[\d\s.,%()±\-–]+", s):
            continue
        keep.append(s)
    return re.sub(r"\s+", " ", " ".join(keep))


def passages(text: str, target=110):
    seen, out = set(), []
    for w in text.split("--- EVIDENCE WINDOW ---"):
        sents = split_sentences(clean_window(w))[1:-1]   # drop cut-off edges
        buf = []
        for s in sents:
            key = s[:60]
            if key in seen:
                buf = []
                continue
            seen.add(key)
            # skip table/figure debris and references
            if re.search(r"\b(Table|Figure|Fig)\s?\d|arXiv|doi|\bet al\.,? \d{4}", s) and len(s.split()) < 12:
                continue
            buf.append(s)
            if sum(len(x.split()) for x in buf) >= target:
                out.append(" ".join(buf))
                buf = []
    return out


def main():
    df = pd.read_csv(SRC)
    rows = []
    for _, r in df.iterrows():
        for p in passages(r["evidence_text"]):
            if "Abstract" in p[:200] or "Proceedings" in p:
                continue
            rows.append({"paper_id": r["paper_id"], "text": p, "label": 0})
    human = pd.DataFrame(rows)
    human["score"] = [score(t)["score"] for t in human.text]

    oof = pd.read_csv(OUT / "detector_oof_predictions.csv")
    ai = oof[(oof.label == 1) & (oof.section != "abstract")]
    ai = ai.assign(score=ai.p_stylo * 100)
    y = [0] * len(human) + [1] * len(ai)
    s = list(human.score) + list(ai.score)
    res = {
        "n_human_body_passages": len(human),
        "n_human_papers": int(human.paper_id.nunique()),
        "n_ai_body_paragraphs": len(ai),
        "auc_body_text_heldout": round(roc_auc_score(y, s), 3),
        "mean_score_human_body": round(human.score.mean(), 1),
        "mean_score_ai_body": round(ai.score.mean(), 1),
        "share_human_body_flagged_ai_at_50": round((human.score > 50).mean(), 3),
        "share_ai_body_flagged_ai_at_50": round((ai.score > 50).mean(), 3),
        "note": "PDF text extraction is noisy (two-column layout); passages may mix columns.",
    }
    human.to_csv(OUT / "heldout_fulltext_passages.csv", index=False)
    (OUT / "heldout_fulltext.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
