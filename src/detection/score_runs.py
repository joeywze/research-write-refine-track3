"""
Score every saved Stage B run with the AI-likeness detector.

For each run in sprint2_demo/runs/ it scores V0, the generic rewrite (V1),
the guided rewrite (V2) and any guided candidates, at paragraph level, and
reports the mean over prose paragraphs and over the paragraphs that changed.

No API calls. Outputs:
  results/detection/run_scores.csv         one row per run x version
  results/detection/paragraph_scores.csv   one row per paragraph x version
  results/detection/run_scores.png         chart for the slides

Usage:  python src/detection/score_runs.py
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detector import score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "sprint2_demo" / "runs"
OUT = ROOT / "results" / "detection"
CITE = re.compile(r"\[\[[^\]]+\]\]")
MIN_WORDS = 40

VERSIONS = [
    ("V0 (initial draft)", "v0_accepted.json"),
    ("V1 generic rewrite", "generic_final.json"),
    ("V2 guided rewrite", "guided_final.json"),
]


def paragraphs(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for p in d["paragraphs"]:
        t = CITE.sub("", p["text"]).strip()
        t = re.sub(r"\s*;\s*\.", ".", t)
        t = re.sub(r"\s+([.,;:])", r"\1", t)
        if len(t.split()) >= MIN_WORDS and not t.lstrip().startswith("|"):
            out[p["paragraph_id"]] = (p["section"], t)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, prow = [], []
    for run in sorted(RUNS.glob("live-*")):
        if not (run / "v0_accepted.json").exists():
            continue
        v0 = paragraphs(run / "v0_accepted.json")
        files = list(VERSIONS) + [
            (f"guided candidate {p.stem.split('_')[1]}", p.name)
            for p in sorted(run.glob("guided_*_candidate.json"))
        ]
        for label, fname in files:
            f = run / fname
            if not f.exists():
                continue
            try:
                paras = paragraphs(f)
            except (KeyError, json.JSONDecodeError):
                continue
            scores, changed = [], []
            for pid, (sec, text) in paras.items():
                s = score(text)["score"]
                is_changed = pid in v0 and v0[pid][1] != text
                scores.append(s)
                if is_changed:
                    changed.append(s)
                prow.append({"run": run.name, "version": label, "paragraph_id": pid,
                             "section": sec, "changed_vs_v0": is_changed, "score": s, "text": text})
            rows.append({"run": run.name, "version": label,
                         "n_paragraphs": len(scores),
                         "n_changed": len(changed),
                         "mean_paragraph_score": round(sum(scores) / len(scores), 1)})
    df = pd.DataFrame(rows)
    pdf = pd.DataFrame(prow)
    df.to_csv(OUT / "run_scores.csv", index=False)
    pdf.to_csv(OUT / "paragraph_scores.csv", index=False)
    print(df.to_string(index=False))

    # changed paragraphs: before vs after
    ch = pdf[pdf.changed_vs_v0 & pdf.version.str.startswith("V2")]
    if len(ch):
        before = pdf[(pdf.version.str.startswith("V0"))].set_index(["run", "paragraph_id"]).score
        ch = ch.assign(v0_score=[before.get((r, p)) for r, p in zip(ch.run, ch.paragraph_id)])
        print("\nParagraphs the guided writer changed:")
        print(ch[["run", "paragraph_id", "section", "v0_score", "score"]].to_string(index=False))
    return df, pdf


if __name__ == "__main__":
    main()
