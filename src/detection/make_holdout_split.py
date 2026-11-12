"""Prepare (and afterwards summarise) a paper-level held-out test for the detector.

Why this exists
---------------
The 0.83 figure in earlier reports was not a true held-out result: the same
papers' abstracts were used in training. Guan Hong's `train_detector.py
--holdout` and `evaluate_holdout.py` fix that, but they need a list of held-out
paper IDs plus two CSV files. This script builds those files (Option A in the
one-day guide: no new API calls).

Split (fixed seed, so anyone can reproduce it)
  * AI side    : 3 of the 10 papers in data/generated/*.csv, every section,
                 split into paragraphs exactly as training does.
  * Human side : the same 3 papers' real abstracts + 150 other random EMNLP
                 abstracts that will also be excluded from training.
Training then still has 7 AI papers and ~1,650 human abstracts.

Usage
  python src/detection/make_holdout_split.py split           # writes evaluation-output/{paper_ids.json,human.csv,generated.csv}
  python src/detection/train_detector.py --holdout evaluation-output/paper_ids.json --output evaluation-output/detector
  python src/detection/evaluate_holdout.py --model evaluation-output/detector/detector_model.json \
      --human evaluation-output/human.csv --generated evaluation-output/generated.csv --output evaluation-output/holdout
  python src/detection/make_holdout_split.py report          # accuracy at 50 + abstract-only AUC

Using all 10 AI papers instead of 3 (paper-grouped cross-validation):
  python src/detection/train_detector.py --output evaluation-output/grouped_cv
  python src/detection/make_holdout_split.py cv               # AUC, 95% interval by paper, per-paper range
Each fold trains without some papers and scores them, so every AI paper is tested once as unseen.
"""

import argparse
import glob
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from detector import split_paragraphs  # noqa: E402
from train_detector import paper_ids  # noqa: E402

ROOT = HERE.parents[1]
OUT = ROOT / "evaluation-output"
MIN_WORDS = 60          # the same minimum train_detector.load_data uses
SEED = 17               # our group number; any fixed value works
N_AI_PAPERS = 3
N_EXTRA_HUMAN = 150


def build_split(out: Path = OUT, seed: int = SEED, n_ai: int = N_AI_PAPERS, n_extra: int = N_EXTRA_HUMAN):
    rng = np.random.default_rng(seed)
    generated = pd.concat([pd.read_csv(f, keep_default_na=False)
                           for f in sorted(glob.glob(str(ROOT / "data" / "generated" / "*.csv")))])
    generated["paper_id"] = paper_ids(generated["paper_id"])
    ai_papers = sorted(generated.paper_id.unique())
    if len(ai_papers) - n_ai < 5:
        raise ValueError("Training needs at least 5 AI papers left after the hold-out")
    held_ai = sorted(rng.choice(ai_papers, size=n_ai, replace=False).tolist())

    human = pd.read_excel(ROOT / "data" / "emnlp_2025_main.xlsx")
    human["paper_id"] = paper_ids(human["paper_id"])
    human = human[human["abstract"].astype(str).str.split().str.len() >= MIN_WORDS]
    others = sorted(set(human.paper_id) - set(ai_papers))
    held_extra = sorted(rng.choice(others, size=n_extra, replace=False).tolist())
    held_human = sorted(set(held_ai) | set(held_extra))

    human_rows = human[human.paper_id.isin(held_human)][["paper_id", "abstract"]]
    human_rows = human_rows.rename(columns={"abstract": "text"})
    ai_rows = []
    for _, r in generated[generated.paper_id.isin(held_ai)].iterrows():
        for paragraph in split_paragraphs(r["text"], MIN_WORDS):
            ai_rows.append({"paper_id": r["paper_id"], "text": paragraph, "section": r["section"]})
    ai_rows = pd.DataFrame(ai_rows)

    ids = sorted(set(human_rows.paper_id) | set(ai_rows.paper_id))
    out.mkdir(parents=True, exist_ok=True)
    (out / "paper_ids.json").write_text(json.dumps(ids, indent=1) + "\n", encoding="utf-8")
    human_rows.to_csv(out / "human.csv", index=False)
    ai_rows[["paper_id", "text"]].to_csv(out / "generated.csv", index=False)
    # Side file so the report can tell abstracts from other sections.
    ai_rows.to_csv(out / "generated_sections.csv", index=False)
    summary = {"seed": seed, "heldout_ai_papers": held_ai, "heldout_paper_count": len(ids),
               "human_passages": len(human_rows), "generated_passages": len(ai_rows)}
    print(json.dumps(summary, indent=2))
    return summary


def auc(labels, scores):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(labels, scores))


def report(out: Path = OUT, threshold: float = 50.0):
    scores = pd.read_csv(out / "holdout" / "scores.csv", keep_default_na=False)
    scores["score"] = scores["score"].astype(float)
    scores["label"] = scores["label"].astype(int)
    sections = pd.read_csv(out / "generated_sections.csv", keep_default_na=False)
    section_of = dict(zip(sections.text, sections.section))
    scores["section"] = [("abstract" if lab == 0 else section_of.get(t, "?"))
                         for lab, t in zip(scores.label, scores.text)]
    predicted_ai = scores.score >= threshold
    human, ai = scores.label == 0, scores.label == 1
    abstracts = scores[scores.section == "abstract"]
    result = {
        "passage_auc_all_sections": auc(scores.label, scores.score),
        f"accuracy_at_{threshold:.0f}": float((predicted_ai == (scores.label == 1)).mean()),
        "balanced_accuracy": float(((predicted_ai & ai).sum() / ai.sum() + (~predicted_ai & human).sum() / human.sum()) / 2),
        "human_flagged_as_ai": f"{int((predicted_ai & human).sum())} of {int(human.sum())}",
        "ai_caught": f"{int((predicted_ai & ai).sum())} of {int(ai.sum())}",
        "abstract_only_auc": auc(abstracts.label, abstracts.score) if abstracts.label.nunique() == 2 else None,
        "abstract_only_counts": {"human": int((abstracts.label == 0).sum()), "ai": int((abstracts.label == 1).sum())},
        "note": "Abstract-only compares like with like; with only a few AI abstracts it is very noisy.",
    }
    (out / "holdout" / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    # evaluation-output/ is gitignored, so keep a small committed copy of the numbers.
    keep = ROOT / "results" / "detection" / "heldout_eval"
    keep.mkdir(parents=True, exist_ok=True)
    (keep / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (keep / "summary.json").write_text((out / "holdout" / "summary.json").read_text(encoding="utf-8"), encoding="utf-8")
    (keep / "paper_ids.json").write_text((out / "paper_ids.json").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def grouped_cv(out: Path = OUT, n_boot: int = 2000, seed: int = SEED):
    """Pool the out-of-fold scores from Guan Hong's paper-grouped CV and add a paper-level interval."""
    from sklearn.metrics import roc_auc_score
    oof = pd.read_csv(out / "grouped_cv" / "detector_oof_predictions.csv", keep_default_na=False)
    oof["label"] = oof["label"].astype(int)
    oof["p_stylo"] = oof["p_stylo"].astype(float)
    by_paper = {p: d for p, d in oof.groupby("paper_id")}
    papers = {lab: oof[oof.label == lab].paper_id.unique() for lab in (0, 1)}
    rng = np.random.default_rng(seed)
    # Resample whole papers (not paragraphs): paragraphs from one paper are not independent.
    boots = []
    for _ in range(n_boot):
        sample = pd.concat([by_paper[p] for lab in (0, 1) for p in rng.choice(papers[lab], len(papers[lab]))])
        boots.append(roc_auc_score(sample.label, sample.p_stylo))
    human = oof[oof.label == 0]
    per_paper = {p: round(float(roc_auc_score(pd.concat([human.label, d.label]), pd.concat([human.p_stylo, d.p_stylo]))), 3)
                 for p, d in oof[oof.label == 1].groupby("paper_id")}
    result = {
        "auc": round(float(roc_auc_score(oof.label, oof.p_stylo)), 3),
        "auc_95ci_by_paper": [round(float(x), 3) for x in np.percentile(boots, [2.5, 97.5])],
        "accuracy_at_50": round(float(((oof.p_stylo >= 0.5) == (oof.label == 1)).mean()), 3),
        "ai_papers": len(papers[1]), "ai_passages": int((oof.label == 1).sum()),
        "human_papers": len(papers[0]),
        "per_ai_paper_auc": dict(sorted(per_paper.items(), key=lambda kv: kv[1])),
        "note": "Every AI paper is scored by a model trained without it. The interval resamples whole papers. "
                "All AI text comes from one generator and prompt, which the interval does not cover.",
    }
    keep = ROOT / "results" / "detection" / "heldout_eval"
    keep.mkdir(parents=True, exist_ok=True)
    (keep / "grouped_cv.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["split", "report", "cv"])
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    {"split": build_split, "report": report, "cv": grouped_cv}[args.step](args.output)


if __name__ == "__main__":
    main()
