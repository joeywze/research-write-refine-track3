"""
Generator -> detector -> reviser loop, with the "just ask nicely" baseline.

Two conditions, run on the same paragraphs for N iterations each:

  naive   : "Rewrite this to sound more human and avoid AI clichés."
            (the obvious shortcut the brief warns plateaus)
  guided  : the reviser gets the detector's diagnosis: which features push the
            score up, and the exact flagged sentences with reasons.

Every candidate must pass a content check (same numbers, same citation tokens,
length within +/-35%) or it is rejected and the previous version kept.
The guided condition also keeps a candidate only if the score does not rise.

Usage:
    export OPENAI_API_KEY=...
    python src/detection/rewrite_loop.py --n 10 --iters 4            # live
    python src/detection/rewrite_loop.py --n 3 --iters 2 --dry-run   # no API, tests plumbing

Outputs (results/detection/):
    loop_log.csv          every attempt: paragraph, condition, iteration, score, accepted
    loop_curve.png        mean score per iteration, naive vs guided
    loop_examples.md      before/after for the paragraphs that improved most
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detector import PLAIN_NAMES, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "detection"
CITE = re.compile(r"\[\[[^\]]+\]\]")
NUM = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*%?")

NAIVE_PROMPT = """Rewrite the following paragraph from a research paper so it sounds more natural and human-written. Avoid AI clichés. Keep every fact, number, citation token like [[S1]] and technical term exactly. Return only the paragraph.

Paragraph:
{text}"""

GUIDED_PROMPT = """You are revising one paragraph of a research paper. A stylometric detector, calibrated on 1,800 real EMNLP 2025 papers, scores it {score:.0f}/100 for "reads like LLM output" (real paper text typically scores 15-40).

What is pushing the score up:
{drivers}

Flagged sentences:
{flagged}

Revise the paragraph to fix these specific problems. Rules:
- Keep every claim, number, citation token like [[S1]] and technical term. Do not add facts, results or citations.
- Keep a hedge only where the claim really is uncertain; say what is uncertain instead of stacking "may/could/potentially".
- Vary sentence length a lot: at least one short, blunt sentence (under 10 words) and, where the logic needs it, one long one.
- Drop "Furthermore/Moreover/Additionally"-style openers when the link is obvious. Break up "X, Y, and Z" lists unless all three items matter.
- Do not replace one stock phrase with another. Plain words are fine.
Return only the revised paragraph.

Paragraph:
{text}"""


def drivers_text(r):
    lines = []
    for name, c in list(r["contributions"].items())[:4]:
        if c > 0.1:
            lines.append(f"- {PLAIN_NAMES.get(name, name)}")
    return "\n".join(lines) or "- nothing major"


def flagged_text(r):
    out = []
    for f in r["flagged"][:6]:
        out.append(f'- "{f["sentence"][:220]}" -> {"; ".join(f["reasons"])}')
    return "\n".join(out) or "- none"


def content_ok(before, after):
    if not after or len(after.split()) < 0.65 * len(before.split()) or len(after.split()) > 1.35 * len(before.split()):
        return False, "length changed too much"
    if sorted(CITE.findall(before)) != sorted(CITE.findall(after)):
        return False, "citations changed"
    if sorted(NUM.findall(CITE.sub("", before))) != sorted(NUM.findall(CITE.sub("", after))):
        return False, "numbers changed"
    return True, ""


class LLM:
    def __init__(self, model, dry_run):
        self.model, self.dry = model, dry_run
        if not dry_run:
            from openai import OpenAI
            self.client = OpenAI()

    def __call__(self, prompt):
        if self.dry:
            m = re.search(r"Paragraph:\n(.*)$", prompt, re.S)
            return m.group(1).strip()
        for attempt in range(3):
            try:
                r = self.client.responses.create(model=self.model, input=prompt)
                return (r.output_text or "").strip()
            except Exception as e:  # noqa: BLE001
                print("  API error:", e)
                time.sleep(3 * (attempt + 1))
        return ""


def pick_paragraphs(n):
    """Highest-scoring prose paragraphs from our real V0 draft, plus GPT pilot paragraphs."""
    rows = []
    ps = OUT / "paragraph_scores.csv"
    if ps.exists():
        p = pd.read_csv(ps)
        last = sorted(p.run.unique())[-1]
        v0 = p[(p.run == last) & p.version.str.startswith("V0")].sort_values("score", ascending=False)
        for _, r in v0.head((n + 1) // 2).iterrows():
            rows.append({"pid": f"V0-{r.paragraph_id}", "source": "our draft V0", "text": r.text})
    oof = pd.read_csv(OUT / "detector_oof_predictions.csv")
    ai = oof[(oof.label == 1) & (oof.section.isin(["introduction", "related_work", "conclusion"]))]
    ai = ai[ai.text.str.split().str.len().between(80, 220)].sort_values("p_stylo", ascending=False)
    for i, (_, r) in enumerate(ai.head(n - len(rows)).iterrows()):
        rows.append({"pid": f"GPT-{r.paper_id[-4:]}-{r.section}-{i}", "source": "GPT pilot", "text": r.text})
    return rows[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--iters", type=int, default=4)
    ap.add_argument("--model", default=os.getenv("REWRITE_MODEL", "gpt-5.6-luna"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    llm = LLM(args.model, args.dry_run)
    paras = pick_paragraphs(args.n)
    log = []
    for p in paras:
        s0 = score(p["text"])
        for cond in ("naive", "guided"):
            cur, cur_r = p["text"], s0
            log.append({**{k: p[k] for k in ("pid", "source")}, "condition": cond, "iteration": 0,
                        "score": cur_r["score"], "accepted": True, "reason": "start", "text": cur})
            for it in range(1, args.iters + 1):
                if cond == "naive":
                    prompt = NAIVE_PROMPT.format(text=cur)
                else:
                    prompt = GUIDED_PROMPT.format(score=cur_r["score"], drivers=drivers_text(cur_r),
                                                  flagged=flagged_text(cur_r), text=cur)
                cand = llm(prompt)
                ok, why = content_ok(cur, cand)
                cand_r = score(cand) if cand else None
                if ok and cond == "guided" and cand_r["score"] > cur_r["score"]:
                    ok, why = False, "score went up"
                if ok:
                    cur, cur_r = cand, cand_r
                log.append({"pid": p["pid"], "source": p["source"], "condition": cond, "iteration": it,
                            "score": cur_r["score"], "candidate_score": cand_r["score"] if cand_r else None,
                            "accepted": ok, "reason": why or "accepted", "text": cur})
                print(f"{p['pid']:28s} {cond:6s} it{it}: {cur_r['score']:5.1f} "
                      f"({'kept' if ok else 'rejected: ' + why})")

    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(log)
    suffix = "_dryrun" if args.dry_run else ""
    df.to_csv(OUT / f"loop_log{suffix}.csv", index=False)

    curve = df.groupby(["condition", "iteration"]).score.mean().unstack(0)
    print("\nMean detector score per iteration:\n", curve.round(1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    colors = {"naive": "#eb6834", "guided": "#2a78d6"}
    names = {"naive": '"Make it sound human" prompt', "guided": "Detector-guided revision"}
    for c in ("naive", "guided"):
        if c in curve:
            ax.plot(curve.index, curve[c], marker="o", lw=2, ms=7, color=colors[c], label=names[c])
            ax.annotate(f"{curve[c].iloc[-1]:.0f}", (curve.index[-1], curve[c].iloc[-1]),
                        xytext=(6, 0), textcoords="offset points", va="center", fontsize=9)
    ax.axhspan(15, 40, color="#2a78d6", alpha=0.08)
    ax.text(0.02, 27, "typical real EMNLP text", fontsize=8, color="#2a78d6", transform=ax.get_yaxis_transform())
    ax.set_xticks(curve.index)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Mean detector score (lower = more human)")
    ax.set_ylim(0, 100)
    ax.set_title(f"Rewriting loop on {len(paras)} paragraphs", loc="left", fontsize=11)
    ax.legend(frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#eee")
    plt.tight_layout()
    plt.savefig(OUT / f"loop_curve{suffix}.png")

    # before/after examples
    last = df[df.iteration == args.iters]
    first = df[df.iteration == 0].set_index(["pid", "condition"])
    lines = ["# Before / after examples (detector-guided)\n"]
    g = last[last.condition == "guided"].copy()
    g["drop"] = [first.loc[(r.pid, "guided")].score - r.score for r in g.itertuples()]
    for r in g.sort_values("drop", ascending=False).head(3).itertuples():
        b = first.loc[(r.pid, "guided")]
        nv = last[(last.pid == r.pid) & (last.condition == "naive")].iloc[0]
        lines += [f"## {r.pid} ({r.source})\n",
                  f"**Before - score {b.score:.0f}**\n\n{b.text}\n",
                  f"**Naive prompt after {args.iters} rounds - score {nv.score:.0f}**\n\n{nv.text}\n",
                  f"**Detector-guided after {args.iters} rounds - score {r.score:.0f}**\n\n{r.text}\n"]
    (OUT / f"loop_examples{suffix}.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved loop_log, loop_curve.png and loop_examples.md to", OUT)


if __name__ == "__main__":
    main()
