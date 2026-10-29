"""
Run the guarded, detector-guided rewrite over every prose paragraph of the V0
paper and write the full revised paper (V3) with its original layout.

    python src/detection/revise_full_paper.py --dry-run     # no API calls, checks wiring
    python src/detection/revise_full_paper.py               # live (~60-100 API calls)

Options: --iters 3 (rounds per paragraph), --threshold 35 (skip paragraphs that
already score below this), --model gpt-5.6-luna.

What is protected
  * Tables (locked in the Stage B handover) and the research-question list are
    never sent to the model.
  * Every rewrite must keep all citation tokens [[S01]], every number, every
    protected technical term from the research package, stay within +/-35% length,
    and pass the fluency guard (no fragments / runs of short sentences).
  * A rewrite is kept only if the detector score does not go up.
  * Progress is saved after each paragraph; re-running resumes instead of paying twice.

Outputs (results/detection/full_paper/):
  final_paper_v3.md      full paper, same headings, tables and citation links as V0
  v0_paper.md            the original, rendered the same way, for side-by-side reading
  revision_report.md     what changed, scores per section and paragraph, hedge removals to check
  paragraphs.csv         one row per paragraph: V0 / V3 text and scores, status
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict, deque
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rewrite_loop as rl  # noqa: E402  (loads .env, prompts, guards)
from detector import HEDGES, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONV = ROOT / "sprint2_demo" / "inputs" / "converted"
OUT = ROOT / "results" / "detection" / "full_paper"
CITATION = re.compile(r"\[\[([A-Za-z][A-Za-z0-9_-]*)\]\]")


def render(paragraphs: dict, manifest: dict) -> str:
    """Same logic as sprint2_demo/handover.py: restore headings, tables, spacing and citation links."""
    blocks = {b["paragraph_id"]: b for b in manifest["blocks"]}
    out = []
    for seg in manifest["layout"]:
        if isinstance(seg, str):
            out.append(seg)
            continue
        pid = seg["paragraph_id"]
        text = paragraphs[pid]
        q = defaultdict(deque)
        for occ in blocks[pid]["citation_occurrences"]:
            q[occ["source_id"]].append(occ["original_markdown"])
        if Counter(CITATION.findall(text)) != Counter(o["source_id"] for o in blocks[pid]["citation_occurrences"]):
            raise ValueError(f"Citations changed in {pid}; cannot render")
        out.append(CITATION.sub(lambda m: q[m[1]].popleft(), text))
    return "".join(out)


def prose_for_scoring(text: str) -> str:
    t = CITATION.sub("", text)
    t = re.sub(r"\s*;\s*\.", ".", t)
    return re.sub(r"\s+([.,;:])", r"\1", t).strip()


def term_counts(text, terms):
    low = text.lower()
    return {t: len(re.findall(r"(?<!\w)" + re.escape(t.lower()) + r"(?!\w)", low)) for t in terms}


def hedge_words(text):
    low = text.lower()
    found = []
    for h in HEDGES:
        n = len(re.findall(r"(?<![\w-])" + re.escape(h) + r"(?![\w-])", low))
        found += [h] * n
    return Counter(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=35.0)
    ap.add_argument("--model", default=rl.os.getenv("REWRITE_MODEL", "gpt-5.6-luna"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fresh", action="store_true", help="ignore saved progress and start again")
    args = ap.parse_args()

    manifest = json.loads((CONV / "handover_manifest.json").read_text(encoding="utf-8"))
    v0 = json.loads((CONV / "v0.json").read_text(encoding="utf-8"))
    package = json.loads((CONV / "research_package.json").read_text(encoding="utf-8"))
    terms = package.get("technical_terms", [])
    blocks = {b["paragraph_id"]: b for b in manifest["blocks"]}

    out = OUT if not args.dry_run else OUT.parent / "full_paper_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    progress_file = out / "progress.json"
    progress = {} if args.fresh or not progress_file.exists() else json.loads(progress_file.read_text(encoding="utf-8"))

    llm = rl.LLM(args.model, args.dry_run)
    rl.GUARD = True
    current = {p["paragraph_id"]: p["text"] for p in v0["paragraphs"]}
    sections = {p["paragraph_id"]: p["section"] for p in v0["paragraphs"]}

    for p in v0["paragraphs"]:
        pid, text = p["paragraph_id"], p["text"]
        b = blocks[pid]
        if pid in progress:
            current[pid] = progress[pid]["v3_text"]
            continue
        rec = {"pid": pid, "section": p["section"], "v0_text": text, "v3_text": text,
               "v0_score": None, "v3_score": None, "status": "", "attempts": []}
        prose = prose_for_scoring(text)
        if b["locked"] or b["kind"] != "prose":
            rec["status"] = f"not revised ({b['kind']}, kept exactly)"
        elif len(prose.split()) < 40:
            rec["status"] = "not revised (too short to score reliably)"
        else:
            r0 = score(prose)
            rec["v0_score"] = r0["score"]
            if r0["score"] < args.threshold:
                rec["status"] = f"not revised (already reads like a real paper, score < {args.threshold:.0f})"
                rec["v3_score"] = r0["score"]
            else:
                cur, cur_r = text, r0
                base_terms = term_counts(text, terms)
                for it in range(1, args.iters + 1):
                    prompt = rl.GUIDED_PROMPT.format(score=cur_r["score"], drivers=rl.drivers_text(cur_r),
                                                     flagged=rl.flagged_text(cur_r), text=cur)
                    cand = llm(prompt)
                    ok, why = rl.content_ok(cur, cand)
                    if ok and term_counts(cand, terms) != base_terms:
                        ok, why = False, "protected technical term changed"
                    if ok:
                        ok, why = rl.fluency_ok(prose_for_scoring(cand))
                    cand_r = score(prose_for_scoring(cand)) if cand else None
                    if ok and cand_r["score"] > cur_r["score"]:
                        ok, why = False, "score went up"
                    rec["attempts"].append({"round": it, "accepted": ok, "reason": why or "accepted",
                                            "candidate_score": cand_r["score"] if cand_r else None})
                    if ok:
                        cur, cur_r = cand, cand_r
                    print(f"{pid} {p['section']:13s} round {it}: {cur_r['score']:5.1f} "
                          f"({'kept' if ok else 'rejected: ' + why})")
                rec["v3_text"], rec["v3_score"] = cur, cur_r["score"]
                if cur != text:
                    rec["status"] = "revised"
                elif args.dry_run:
                    rec["status"] = "dry run (no rewrite attempted)"
                else:
                    rec["status"] = "not revised (all rewrites rejected)"
        current[pid] = rec["v3_text"]
        progress[pid] = rec
        progress_file.write_text(json.dumps(progress, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------ outputs
    v0_md = render({p["paragraph_id"]: p["text"] for p in v0["paragraphs"]}, manifest)
    v3_md = render(current, manifest)
    v3_md = re.sub(r"Draft V0 — revised [^.]*\.",
                   f"Draft V3 — detector-guided revision of V0, {date.today():%d %B %Y}.", v3_md, count=1)
    (out / "v0_paper.md").write_text(v0_md, encoding="utf-8")
    (out / "final_paper_v3.md").write_text(v3_md, encoding="utf-8")

    rows = list(progress.values())
    df = pd.DataFrame([{k: r[k] for k in ("pid", "section", "status", "v0_score", "v3_score", "v0_text", "v3_text")}
                       for r in rows])
    df.to_csv(out / "paragraphs.csv", index=False)

    scored = df.dropna(subset=["v0_score"]).copy()
    scored["v3_score"] = scored.v3_score.fillna(scored.v0_score)
    rev = df[df.status == "revised"]

    L = ["# Full-paper revision report (V0 → V3)", "",
         "*Generated by `src/detection/revise_full_paper.py`. "
         + ("DRY RUN: no API calls were made, so nothing was rewritten.* " if args.dry_run else "*"), "",
         "## What this is", "",
         "Our detector-guided rewriting loop was run over **every prose paragraph** of the team's draft paper "
         "(V0). Each paragraph that read as AI-like (detector score ≥ "
         f"{args.threshold:.0f}) got up to {args.iters} rounds of revision. Tables and the research-question "
         "list were never sent to the model. A rewrite was kept only if it kept every citation, number and "
         "protected technical term, changed length by less than 35%, passed the fluency guard, and did not "
         "raise the detector score. The full revised paper is `final_paper_v3.md`; the original, rendered the "
         "same way, is `v0_paper.md`.", "",
         "**Detector score:** 0 = reads like a real EMNLP paper, 100 = reads like GPT. Real paper text has a "
         "median of about 28 (middle half 15-39); raw GPT paragraphs have a median of about 61.", "",
         "## Headline", "",
         "| | V0 | V3 |", "|---|---|---|",
         f"| Mean detector score over {len(scored)} scorable paragraphs | {scored.v0_score.mean():.1f} | "
         f"{scored.v3_score.mean():.1f} |",
         f"| Paragraphs scoring ≥ 50 (AI-like) | {(scored.v0_score >= 50).sum()} | {(scored.v3_score >= 50).sum()} |",
         f"| Paragraphs revised | | {len(rev)} of {len(df)} |", "",
         "## By section", "", "| Section | Paragraphs scored | V0 mean | V3 mean |", "|---|---|---|---|"]
    order = ["abstract", "introduction", "related_work", "methodology", "experiments", "conclusion"]
    for sec in order:
        s = scored[scored.section == sec]
        if len(s):
            L.append(f"| {sec.replace('_', ' ').title()} | {len(s)} | {s.v0_score.mean():.1f} | {s.v3_score.mean():.1f} |")

    L += ["", "## Paragraph by paragraph", "",
          "| Paragraph | Section | V0 | V3 | Status |", "|---|---|---|---|---|"]
    for r in df.itertuples():
        v0s = "" if pd.isna(r.v0_score) else f"{r.v0_score:.0f}"
        v3s = "" if pd.isna(r.v3_score) else f"{r.v3_score:.0f}"
        L.append(f"| {r.pid} | {r.section.replace('_', ' ')} | {v0s} | {v3s} | {r.status} |")

    rej = Counter(a["reason"] for r in rows for a in r["attempts"] if not a["accepted"])
    if rej:
        L += ["", "## Rewrites rejected by the safety checks", "", "| Reason | Count |", "|---|---|"]
        L += [f"| {k} | {v} |" for k, v in rej.most_common()]

    L += ["", "## Please check: hedges removed", "",
          "Cutting hedge words lowers the detector score, but it can also turn a tentative claim into a definite "
          "one. These revised paragraphs lost hedge words; read each one and restore the hedge if the original "
          "uncertainty was real.", ""]
    flagged = 0
    for r in rows:
        if r["status"] != "revised":
            continue
        lost = hedge_words(r["v0_text"]) - hedge_words(r["v3_text"])
        if lost:
            flagged += 1
            L += [f"### {r['pid']} ({r['section'].replace('_', ' ')}): removed {', '.join(sorted(lost.elements()))}",
                  "", f"**V0 ({r['v0_score']:.0f}):** {prose_for_scoring(r['v0_text'])}", "",
                  f"**V3 ({r['v3_score']:.0f}):** {prose_for_scoring(r['v3_text'])}", ""]
    if not flagged:
        L.append("*No revised paragraph lost hedge words.*")

    L += ["", "## All revised paragraphs, before and after", ""]
    for r in rows:
        if r["status"] == "revised":
            L += [f"### {r['pid']} ({r['section'].replace('_', ' ')}): {r['v0_score']:.0f} → {r['v3_score']:.0f}", "",
                  f"**Before:** {prose_for_scoring(r['v0_text'])}", "",
                  f"**After:** {prose_for_scoring(r['v3_text'])}", ""]
    L += ["", "## Limitations", "",
          "- The loop optimises against our own detector; a lower score is not proof the text reads more human. "
          "The human evaluation tests that.",
          "- The automatic checks protect numbers, citations and technical terms, not meaning. Claims can still "
          "shift (see the hedge section above); Stage B's semantic preservation checker should be run on V3 "
          "before it is treated as final.",
          "- One draft, one model, one run."]
    (out / "revision_report.md").write_text("\n".join(L), encoding="utf-8")

    print(f"\nMean detector score: V0 {scored.v0_score.mean():.1f} -> V3 {scored.v3_score.mean():.1f} "
          f"({len(rev)} of {len(df)} paragraphs revised)")
    print(f"Saved final_paper_v3.md, v0_paper.md, revision_report.md and paragraphs.csv to {out}")


if __name__ == "__main__":
    main()
