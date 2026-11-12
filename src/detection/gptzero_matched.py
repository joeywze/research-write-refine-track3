"""GPTZero vs our detector on the human-study v2 set: 10 real paragraphs and 10 AI-generated ones.

Same 20 short texts the raters see (50-80 words, no citations, half abstracts and half body
text on each side), so real and AI text are matched on length and genre. That makes this a
fairer "against real text" comparison than real abstracts vs our pipeline paragraphs.

Step 1 - make the sheet:
    python src/detection/gptzero_matched.py export
  writes .private/human_eval_v2/gptzero_matched.csv (gitignored: it shows which items are real,
  so it must not reach the raters while the study is open). Rows are in form order (Item 01-20).

Step 2 - paste each `text` into https://gptzero.me and type its three numbers into
  gptzero_ai, gptzero_mixed and gptzero_human (e.g. 100, 0, 0; a % sign is fine). Save as CSV UTF-8.
  Running `export` again keeps any scores you have already typed in.

Step 3 - summarise:
    python src/detection/gptzero_matched.py summarise
  writes results/detection/human_eval_v2/gptzero_matched_summary.json (averages only, safe to commit).

Note: `our_score` is the recorded detector's score. These papers may be in its training data, so
it is a best case for our detector; GPTZero has never seen our labels.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
STUDIES = {  # study -> (answer key, GPTZero sheet, summary)
    "v2": (ROOT / ".private" / "human_eval_v2" / "PRIVATE_answer_key.csv",
           ROOT / ".private" / "human_eval_v2" / "gptzero_matched.csv",
           ROOT / "results" / "detection" / "human_eval_v2" / "gptzero_matched_summary.json"),
    "v3": (ROOT / ".private" / "human_eval_v3" / "PRIVATE_answer_key.csv",
           ROOT / ".private" / "human_eval_v3" / "gptzero_pipeline.csv",
           ROOT / "results" / "detection" / "human_eval_v3" / "gptzero_pipeline_summary.json"),
}
KEY, SHEET, SUMMARY = STUDIES["v3"]
SCORES = ["gptzero_ai", "gptzero_mixed", "gptzero_human"]


def number(series):
    return pd.to_numeric(series.astype(str).str.replace("%", "").str.strip(), errors="coerce")


def export():
    if not KEY.exists():
        raise SystemExit(f"No answer key at {KEY.relative_to(ROOT)}. Run src/detection/human_eval_matched.py first.")
    key = pd.read_csv(KEY, keep_default_na=False, encoding="utf-8-sig")
    table = key.rename(columns={"detector_score": "our_score"})[
        ["item_id", "truth", "section", "words", "our_score", "text"]].copy()
    for col in SCORES:
        table[col] = ""
    if SHEET.exists():  # keep scores already typed in
        old = pd.read_csv(SHEET, keep_default_na=False, encoding="utf-8-sig").set_index("item_id")
        for col in SCORES:
            if col in old:
                table[col] = table.item_id.map(old[col].astype(str)).fillna("")
    table.to_csv(SHEET, index=False, encoding="utf-8-sig")
    todo = int((table.gptzero_ai.astype(str).str.strip() == "").sum())
    print(f"Wrote {len(table)} texts to {SHEET.relative_to(ROOT)} ({todo} still to score on gptzero.me).")


def auc(labels, scores):
    """Chance that a random AI text scores higher than a random real one (ties count half)."""
    ai = [s for l, s in zip(labels, scores) if l == 1]
    real = [s for l, s in zip(labels, scores) if l == 0]
    wins = sum((a > r) + 0.5 * (a == r) for a in ai for r in real)
    return round(wins / (len(ai) * len(real)), 2)


def summarise():
    table = pd.read_csv(SHEET, keep_default_na=False, encoding="utf-8-sig")
    for col in SCORES + ["our_score"]:
        table[col] = number(table[col])
    missing = table[table.gptzero_ai.isna()]
    if len(missing):
        raise SystemExit(f"{len(missing)} rows have no gptzero_ai yet, e.g. {missing.iloc[0]['item_id']}.")
    table["label"] = (table.truth == "generated").astype(int)
    table["gptzero_label"] = table[SCORES].idxmax(axis=1).str.replace("gptzero_", "")
    group = {"real": table[table.truth == "real"], "generated": table[table.truth == "generated"]}
    result = {
        "texts": {name: int(len(g)) for name, g in group.items()},
        "our_detector_mean": {name: round(float(g.our_score.mean()), 1) for name, g in group.items()},
        "gptzero_ai_mean": {name: round(float(g.gptzero_ai.mean()), 1) for name, g in group.items()},
        "gptzero_labels": {name: g.gptzero_label.value_counts().to_dict() for name, g in group.items()},
        "auc_real_vs_generated": {"our_detector": auc(table.label, table.our_score),
                                  "gptzero": auc(table.label, table.gptzero_ai)},
        "accuracy_at_50": {"our_detector": round(float(((table.our_score >= 50) == (table.label == 1)).mean()), 2),
                           "gptzero": round(float(((table.gptzero_ai >= 50) == (table.label == 1)).mean()), 2)},
        "note": (f"Human-study {SUMMARY.parent.name[-2:]} texts: 10 real EMNLP 2025 + 10 AI (v2: gpt-5.6-luna; v3: our pipeline), 50-80 words, matched genre. "
                 "GPTZero = free website. Our score = recorded detector (papers may be in training: best case). "
                 "n=20, so treat as indicative."),
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["export", "summarise"])
    parser.add_argument("--study", choices=sorted(STUDIES), default="v3",
                        help="v3 (default) = .private/human_eval_v3/gptzero_pipeline.csv, our final papers vs real text; "
                             "v2 = the earlier sheet with outside AI text")
    args = parser.parse_args(argv)
    global KEY, SHEET, SUMMARY
    KEY, SHEET, SUMMARY = STUDIES[args.study]
    export() if args.step == "export" else summarise()


if __name__ == "__main__":
    main()
