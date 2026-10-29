"""
Human evaluation: can people tell real paper paragraphs from generated ones?

    python src/detection/human_eval.py build   # makes the form text + private answer key
    python src/detection/human_eval.py score responses.csv

Design
  * 12 paragraphs, all on the same topic (LLM-as-a-judge evaluation) so topic
    gives nothing away:
      6 real  : passages from the full text of real EMNLP 2025 papers (Cluster 7)
      3 gen-v0: paragraphs from our generated draft V0
      3 gen-rev: the same kind of paragraphs after the detector-guided loop
                 (taken from results/detection/loop_log.csv once you have run
                 rewrite_loop.py; falls back to V0 paragraphs if not)
  * Citations, equation debris and hyphenation are stripped from every item so
    formatting is not a tell. Lengths are matched (70-140 words).
  * Raters answer "Real paper" or "Generated" and a 1-5 confidence.

Scoring reports overall detection accuracy with a 95% Wilson interval,
accuracy separately for V0 and revised items (the number that matters), and
per-rater accuracy. 50% = raters are guessing (the target).

responses.csv format (export from Google Forms works after renaming columns):
    rater_id, item_id, answer            # answer = "real" or "generated"
or the wide Google Forms layout: one row per rater, one column per item
named "Item 01", "Item 02", ... (we detect this automatically).
"""

import math
import random
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "detection" / "human_eval"
SEED = 7


def tidy(t: str) -> str:
    t = re.sub(r"\[\[[^\]]+\]\]", "", t)
    t = re.sub(r"\([^()]*\b(19|20)\d{2}[a-z]?\)", "", t)          # (Author et al., 2024)
    t = re.sub(r"\*\*|__", "", t)
    t = re.sub(r"\s*;\s*\.", ".", t)
    t = re.sub(r"\.{2,}$", ".", t)
    t = re.sub(r"\s+([.,;:])", r"\1", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()


def clean_enough(t: str) -> bool:
    n = len(t.split())
    if not 70 <= n <= 140:
        return False
    if re.search(r"Table|Figure|Fig\.|Appendix|Section \d|§|=|\d+\.\d+\.\d|https?:", t):
        return False
    if not t.endswith("."):
        return False
    if re.search(r"\b[a-z]+[A-Z][a-z]+\b", t):   # column-merge debris like "settingsThe"
        return False
    if re.search(r"\w- \w", t):                   # broken hyphenation "in- troduce"
        return False
    if re.search(r"\b(\w+) \1\b", t):              # repeated heading word "Relevance Relevance"
        return False
    if re.search(r"\(\d\)|prior work|et al|\d{4}|LLMbased|selfpreference", t):
        return False
    if re.search(r"[a-z] [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+", t):   # heading run into a sentence
        return False
    if re.search(r"[a-z]{3,}[A-Z]|[{}]|\b[a-z]\d? [a-z]\d?\b", t):
        return False
    return True


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    curated = ROOT / "data/human_eval/real_passages_curated.csv"
    # Hand-checked passages (PDF debris such as run-in headings removed). Falls back to auto-filter.
    real = pd.read_csv(curated if curated.exists() else ROOT / "results/detection/heldout_fulltext_passages.csv")
    real_items = [tidy(t) for t in real.text if not re.search(r"\([^()]*\b(19|20)\d{2}", t)]
    if not curated.exists():
        real_items = [t for t in real_items if clean_enough(t)]
    rng.shuffle(real_items)

    para = pd.read_csv(ROOT / "results/detection/paragraph_scores.csv")
    last = sorted(para.run.unique())[-1]
    v0 = para[(para.run == last) & para.version.str.startswith("V0")]
    v0_items = [(pid, tidy(t)) for pid, t in zip(v0.paragraph_id, v0.text)]
    v0_items = [(p, t) for p, t in v0_items if 60 <= len(t.split()) <= 160]
    rng.shuffle(v0_items)

    rev_items = []
    log = ROOT / "results/detection/loop_log.csv"
    if log.exists():
        lg = pd.read_csv(log)
        mx = lg.iteration.max()
        g = lg[(lg.condition == "guided") & lg.pid.str.startswith("V0-")]
        start = g[g.iteration == 0].set_index("pid").text
        fin = g[g.iteration == mx]
        # only paragraphs the loop actually changed (all-rejected ones are still V0)
        rev_items = [(p, tidy(t)) for p, t in zip(fin.pid, fin.text) if t != start.get(p)]
        rng.shuffle(rev_items)
    used = {p.replace("V0-", "") for p, _ in rev_items[:3]}
    v0_pick = [x for x in v0_items if x[0] not in used][:3]
    rev_pick = rev_items[:3] if len(rev_items) >= 3 else v0_items[3:6]
    rev_label = "generated_revised" if len(rev_items) >= 3 else "generated_v0"

    items = ([("real", "cluster7_fulltext", t) for t in real_items[:6]]
             + [("generated_v0", p, t) for p, t in v0_pick]
             + [(rev_label, p, t) for p, t in rev_pick])
    rng.shuffle(items)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from detector import score as detector_score

    key, form = [], ["# Real or generated?\n",
                     "Each paragraph below is either from a published EMNLP 2025 paper or was generated "
                     "with an LLM for our project. All are about evaluating LLMs as judges; citations were "
                     "removed from all of them. For each one choose **Real paper** or **Generated**, and how "
                     "confident you are (1 = guess, 5 = certain). Optional: one phrase that gave it away.\n"]
    for i, (label, src, text) in enumerate(items, 1):
        iid = f"Item {i:02d}"
        key.append({"item_id": iid, "truth": "real" if label == "real" else "generated",
                    "condition": label, "source": src, "words": len(text.split()),
                    "detector_score": detector_score(text)["score"], "text": text})
        form.append(f"## {iid}\n\n{text}\n\n- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________\n")
    (OUT / "form_for_raters.md").write_text("\n".join(form), encoding="utf-8")
    pd.DataFrame(key).to_csv(OUT / "PRIVATE_answer_key.csv", index=False)
    template = pd.DataFrame([{"rater_id": f"R{r}", "item_id": k["item_id"], "answer": "", "confidence": ""}
                             for r in range(1, 4) for k in key])
    template.to_csv(OUT / "responses_template.csv", index=False)
    print(f"Built {len(items)} items -> {OUT}")
    print(pd.DataFrame(key).groupby("condition").agg(items=("item_id", "count"),
                                                     mean_detector_score=("detector_score", "mean")).round(1).to_string())
    if rev_label != "generated_revised":
        print("NOTE: fewer than 3 changed paragraphs in loop_log.csv, so the 'revised' slots use V0 "
              "paragraphs. Run rewrite_loop.py first, then rebuild.")


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def normalise(ans):
    a = str(ans).strip().lower()
    if a.startswith("real") or a.startswith("human"):
        return "real"
    if a.startswith("gen") or a.startswith("ai") or a.startswith("llm"):
        return "generated"
    return None


def score_responses(path):
    key = pd.read_csv(OUT / "PRIVATE_answer_key.csv")
    r = pd.read_csv(path)
    if "item_id" not in r.columns:  # wide Google Forms export: one row per rater
        rows = []
        for i, resp in enumerate(r.to_dict("records")):
            rid = f"R{i + 1}"          # anonymised: names are never saved
            by_item = {}
            for col, val in resp.items():
                m = re.search(r"(Item \d+)", str(col))
                if not m:
                    continue
                slot = by_item.setdefault(m.group(1), {})
                c = str(col).strip()
                if re.match(r"Item \d+", c):
                    slot["answer"] = val
                elif c.lower().startswith("confidence"):
                    slot["confidence"] = val
                else:
                    slot["reason"] = val
            for item, slot in by_item.items():
                rows.append({"rater_id": rid, "item_id": item, **slot})
        r = pd.DataFrame(rows)
    else:
        codes = {v: f"R{i + 1}" for i, v in enumerate(dict.fromkeys(r.rater_id))}
        r["rater_id"] = r.rater_id.map(codes)
    r["answer"] = r.answer.map(normalise)
    r = r.dropna(subset=["answer"]).merge(key[["item_id", "truth", "condition"]], on="item_id")
    r["correct"] = r.answer == r.truth

    def line(df, name):
        k, n = int(df.correct.sum()), len(df)
        lo, hi = wilson(k, n)
        return {"group": name, "correct": k, "n": n, "accuracy": round(k / n, 3) if n else None,
                "ci95_low": round(lo, 3), "ci95_high": round(hi, 3)}

    rows = [line(r, "ALL items (detection accuracy)")]
    for c in ["real", "generated_v0", "generated_revised"]:
        sub = r[r.condition == c]
        if len(sub):
            rows.append(line(sub, f"{c} items"))
    for rid, sub in r.groupby("rater_id"):
        rows.append(line(sub, f"rater {rid}"))
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "human_eval_results.csv", index=False)
    print(res.to_string(index=False))
    print("\n50% = raters cannot tell (target). For generated items, accuracy = share correctly called 'generated'.")
    r["said_generated"] = r.answer == "generated"
    per_item = (r.groupby(["item_id", "condition"])
                .agg(share_said_generated=("said_generated", "mean"), accuracy=("correct", "mean"))
                .reset_index())
    if "detector_score" in key.columns:
        per_item = per_item.merge(key[["item_id", "detector_score"]], on="item_id")
        rho = per_item[["detector_score", "share_said_generated"]].corr(method="spearman").iloc[0, 1]
        print(f"\nDetector vs humans: Spearman correlation between an item's detector score and the share "
              f"of raters who called it generated = {rho:.2f} (over {len(per_item)} items)")
        print(per_item.groupby("condition")[["detector_score", "share_said_generated"]].mean().round(2).to_string())
    per_item.to_csv(OUT / "human_eval_per_item.csv", index=False)

    if "reason" in r.columns:
        names = {"real": "Real paper", "generated_v0": "First draft (unrevised)",
                 "generated_revised": "Final paper (detector-guided)"}
        cols = [c for c in ("item_id", "condition", "rater_id", "answer", "correct", "confidence", "reason") if c in r]
        reasons = r[cols].copy()
        reasons["condition"] = reasons.condition.map(names).fillna(reasons.condition)
        reasons = reasons[reasons.reason.astype(str).str.strip().ne("") & reasons.reason.notna()]
        reasons.sort_values(["condition", "item_id", "rater_id"]).to_csv(OUT / "human_eval_reasons.csv", index=False)
        print(f"\nSaved {len(reasons)} rater reasons (anonymised) to human_eval_reasons.csv")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build()
    elif len(sys.argv) >= 3 and sys.argv[1] == "score":
        score_responses(sys.argv[2])
    else:
        print(__doc__)
