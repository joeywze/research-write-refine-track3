"""Half 2 pipeline: detector-guided rewriting with every content check in front of it.

    V0 + research package
      -> score every editable paragraph with the stylometric detector
      -> (optional) Guan Hong's context critic reviews the draft once and gives leads
      -> for each AI-like paragraph, up to 3 attempts:
           rewrite (detector feedback + critic leads + why the last try failed)
           -> fluency guard -> preservation rules -> no new facts
           -> evidence check (LLM) -> meaning check (LLM)
           -> keep it only if every check passes and the score does not go up
      -> after 3 failed attempts the original paragraph is kept
      -> final paper + change report (what changed, why, which checks passed)

The detector chooses WHAT to rewrite and gives style feedback. It never decides
whether a rewrite is safe: only the content checks can accept a rewrite.

Usage (from sprint2_demo/):
  python half2_pipeline.py --plan                                   # offline: which paragraphs would be revised
  python half2_pipeline.py --output runs/half2-<date> --writer-model <m1> --checker-model <m2> \
      [--critic-model <m3>] [--paragraphs P002,P027] [--max-paragraphs 4]
"""

import argparse
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

from handover import render
from project_io import read_input
from src.writing.contracts import digest
from src.writing.preservation import SemanticGate
from src.writing.providers import OpenAIJSON, TokenBudget
from src.writing.storage import RunStore

import half2_checks as checks
from half2_checks import rl

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs" / "converted"
MODEL_FILE = HERE.parent / "results" / "detection" / "detector_model.json"
MAX_ATTEMPTS = 3
THRESHOLD = 35.0
MIN_WORDS = 40

REWRITE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["paragraph"],
                  "properties": {"paragraph": {"type": "string"}}}


def score(text, model):
    return rl.score(checks.plain(text), model)


def editable_ids(manifest):
    return {b["paragraph_id"] for b in manifest["blocks"] if b["kind"] == "prose" and not b["locked"]}


def select(v0, manifest, model, threshold=THRESHOLD, only=None, limit=None):
    """Paragraphs to rewrite: editable prose, long enough to score, and AI-like."""
    editable = editable_ids(manifest)
    rows = []
    for p in v0.paragraphs:
        if p.paragraph_id not in editable or (only and p.paragraph_id not in only):
            continue
        if len(checks.plain(p.text).split()) < MIN_WORDS:
            continue
        result = score(p.text, model)
        if only or result["score"] >= threshold:
            rows.append((p.paragraph_id, result))
    rows.sort(key=lambda row: -row[1]["score"])
    return rows[:limit] if limit else rows


def critic_leads(critique):
    """ACTIONABLE findings per paragraph from Guan Hong's critic, as short notes for the writer."""
    leads = {}
    for row in (critique or {}).get("paragraphs", []):
        for f in row["findings"]:
            if f["status"] == "ACTIONABLE":
                leads.setdefault(row["paragraph_id"], []).append(
                    f'{f["criterion"]}: {f["explanation"]} Suggested: {f["safe_action"]}'.strip())
    return leads


def instructions(result, leads, last_rejection):
    rules = rl.GUIDED_PROMPT.split("Paragraph:")[0].format(
        score=result["score"], drivers=rl.drivers_text(result), flagged=rl.flagged_text(result))
    extra = []
    if leads:
        extra.append("A content reviewer also noted (fix these only if you can without adding facts):\n"
                     + "\n".join(f"- {lead}" for lead in leads))
    if last_rejection:
        extra.append(f"Your previous attempt was rejected: {last_rejection}. Fix that problem this time.")
    extra.append('Keep [[S01]]-style citation tokens exactly. Return JSON: {"paragraph": "<revised paragraph>"}.')
    rules = rules.replace("Return only the revised paragraph.", "").strip()
    return rules + "\n\n" + "\n\n".join(extra)


def revise_paragraph(package, v0, current, pid, result, model, writer, *, evidence_gate, semantic_gate,
                     leads=(), attempts=MAX_ATTEMPTS, progress=None):
    original = checks.paragraph(current, pid).text
    record = {"paragraph_id": pid, "section": checks.paragraph(v0, pid).section,
              "score_before": result["score"],
              "top_features": [rl.PLAIN_NAMES.get(k, k) for k, v in result["contributions"].items() if v > 0.1][:3],
              "critic_leads": list(leads), "attempts": [], "outcome": "kept original",
              "text_before": original, "text_after": original, "score_after": result["score"]}
    last_rejection = ""
    for attempt in range(1, attempts + 1):
        try:
            response = writer.generate("half2_rewrite", instructions(result, leads, last_rejection),
                                       {"paragraph": original}, REWRITE_SCHEMA, 4000)
            candidate = str(response.get("paragraph", "")).strip()
        except Exception as error:  # a failed model call is a failed attempt, never a pass
            candidate, results = "", [checks.CheckResult("writer", "CHECK_ERROR", f"{type(error).__name__}: {error}")]
        else:
            results = checks.check_rewrite(package, v0, current, pid, candidate,
                                           evidence_gate=evidence_gate, semantic_gate=semantic_gate)
        if candidate and candidate == original:
            results = [checks.CheckResult("writer", "NO_CHANGE", "the rewrite was identical to the original")]
        new_score = score(candidate, model)["score"] if candidate else None
        passed = bool(results) and all(r.passed for r in results)
        if passed and new_score is not None and new_score > result["score"]:
            passed, results = False, results + [checks.CheckResult(
                "detector", "NO_IMPROVEMENT", f"score went up ({result['score']:.0f} -> {new_score:.0f})")]
        record["attempts"].append({"attempt": attempt, "text": candidate, "score": new_score,
                                   "accepted": passed, "checks": checks.as_dicts(results),
                                   "verdict": checks.summary(results)})
        if progress:
            progress(pid, attempt, passed, checks.summary(results), new_score)
        if passed:
            record.update(outcome="revised", text_after=candidate, score_after=new_score)
            return record, checks.with_paragraph(current, pid, candidate)
        last_rejection = checks.summary(results).replace("rejected by ", "")
    return record, current


def run(package, v0, manifest, model, writer, store, *, evidence_gate=None, semantic_gate=None, critic=None,
        threshold=THRESHOLD, only=None, limit=None, progress=None):
    start = perf_counter()
    targets = select(v0, manifest, model, threshold, only, limit)
    leads = {}
    if critic is not None:
        leads = critic_leads(critic.assess(package, v0, "v0_review", store))
    current, records = v0, []
    for pid, result in targets:
        record, current = revise_paragraph(package, v0, current, pid, result, model, writer,
                                           evidence_gate=evidence_gate, semantic_gate=semantic_gate,
                                           leads=leads.get(pid, ()), progress=progress)
        records.append(record)
    after_leads = None
    if critic is not None and current != v0:
        after_leads = critic_leads(critic.assess(package, current, "final_review", store))
    store.write("final_draft.json", current)
    (store.directory / "final_paper.md").write_text(render(current, manifest), encoding="utf-8")
    report = {
        "interpretation": "The detector chose paragraphs and gave feedback; only the content checks could accept a rewrite.",
        "threshold": threshold,
        "paragraphs": records,
        "totals": {"selected": len(records),
                   "revised": sum(r["outcome"] == "revised" for r in records),
                   "kept_original": sum(r["outcome"] != "revised" for r in records),
                   "attempts": sum(len(r["attempts"]) for r in records),
                   "mean_score_before": mean([r["score_before"] for r in records]),
                   "mean_score_after": mean([r["score_after"] for r in records])},
        "critic": None if critic is None else {
            "actionable_before": sum(len(v) for v in leads.values()),
            "actionable_after": None if after_leads is None else sum(len(v) for v in after_leads.values())},
    }
    store.write("change_report.json", report)
    (store.directory / "change_report.md").write_text(as_markdown(report), encoding="utf-8")
    store.write("run_summary.json", {
        "v0_hash": digest(v0), "final_hash": digest(current), "package_hash": digest(package),
        "detector_model_hash": digest(model), "writer_model": writer.model,
        "checker_model": getattr(semantic_gate, "model", None), "evidence_model": getattr(evidence_gate, "model", None),
        "critic_model": getattr(critic, "model", None), "elapsed_seconds": round(perf_counter() - start, 1),
        "test_only": getattr(writer, "test_only", False)})
    return report, current


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else None


def as_markdown(report):
    t = report["totals"]
    lines = ["# Half 2 change report", "",
             f"{t['revised']} of {t['selected']} selected paragraphs revised; {t['kept_original']} kept as written. "
             f"Mean detector score on selected paragraphs: {t['mean_score_before']} -> {t['mean_score_after']}.", "",
             "| Paragraph | Score | Outcome | Attempts | Last verdict |", "|---|---|---|---|---|"]
    for r in report["paragraphs"]:
        last = r["attempts"][-1]["verdict"] if r["attempts"] else ""
        lines.append(f"| {r['paragraph_id']} | {r['score_before']:.0f} -> {r['score_after']:.0f} | {r['outcome']} "
                     f"| {len(r['attempts'])} | {last} |")
    for r in report["paragraphs"]:
        lines += ["", f"## {r['paragraph_id']} ({r['section'].replace('_', ' ')})", "",
                  f"Why selected: detector score {r['score_before']:.0f}; "
                  + (", ".join(r["top_features"]) or "no single dominant feature") + "."]
        if r["critic_leads"]:
            lines.append("Reviewer leads: " + " | ".join(r["critic_leads"]))
        for a in r["attempts"]:
            lines.append(f"- Attempt {a['attempt']}: {a['verdict']}")
        lines += ["", f"**Before:** {checks.plain(r['text_before'])}", "",
                  f"**After:** {checks.plain(r['text_after'])}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", type=Path, default=INPUTS)
    parser.add_argument("--detector-model", type=Path, default=MODEL_FILE)
    parser.add_argument("--plan", action="store_true", help="offline: list the paragraphs that would be revised")
    parser.add_argument("--output", type=Path, help="new run directory")
    parser.add_argument("--writer-model")
    parser.add_argument("--checker-model", help="evidence and meaning checks (must differ from the writer)")
    parser.add_argument("--critic-model", help="optional: Guan Hong's context critic before and after")
    parser.add_argument("--paragraphs", help="comma-separated IDs to revise, e.g. P002,P027 (demo / hard case)")
    parser.add_argument("--max-paragraphs", type=int)
    parser.add_argument("--threshold", type=float, default=THRESHOLD)
    parser.add_argument("--token-limit", type=int, default=1_500_000)
    args = parser.parse_args(argv)
    package, v0, manifest = read_input(args.inputs)
    model = json.loads(args.detector_model.read_text(encoding="utf-8"))
    only = set(args.paragraphs.split(",")) if args.paragraphs else None
    if args.plan:
        rows = select(v0, manifest, model, args.threshold, only, args.max_paragraphs)
        print(json.dumps([{"paragraph_id": pid, "score": r["score"],
                           "top_features": [rl.PLAIN_NAMES.get(k, k) for k, v in r["contributions"].items() if v > 0.1][:3]}
                          for pid, r in rows], indent=2))
        return
    if not (args.output and args.writer_model and args.checker_model):
        parser.error("a live run needs --output, --writer-model and --checker-model")
    if args.writer_model.strip().casefold() in {m.strip().casefold() for m in (args.checker_model, args.critic_model) if m}:
        parser.error("use a different model to check the writer's output")
    store = RunStore(args.output)
    budget = TokenBudget(args.token_limit)
    writer = OpenAIJSON(args.writer_model, budget, store, stage="writer")
    evidence_gate = checks.EvidenceGate(OpenAIJSON(args.checker_model, budget, store, stage="evidence"),
                                        checks.EvidenceIndex(package))
    semantic_gate = SemanticGate(OpenAIJSON(args.checker_model, budget, store, stage="preservation"))
    critic = None
    if args.critic_model:
        from src.writing.critic import QualitativeCritic
        from refine_accepted import detector_hints
        editable = editable_ids(manifest)
        critic = QualitativeCritic(OpenAIJSON(args.critic_model, budget, store, stage="critique"),
                                   detector_hints=lambda d: detector_hints(d, model, editable),
                                   editable_ids=sorted(editable))

    def progress(pid, attempt, ok, verdict, new_score):
        print(f"{datetime.now():%H:%M:%S} {pid} attempt {attempt}: {'ACCEPTED' if ok else 'rejected'} - {verdict}")

    report, _ = run(package, v0, manifest, model, writer, store, evidence_gate=evidence_gate,
                    semantic_gate=semantic_gate, critic=critic, threshold=args.threshold, only=only,
                    limit=args.max_paragraphs, progress=progress)
    print(json.dumps(report["totals"], indent=2))
    print(f"Saved final_paper.md and change_report.md to {store.directory}")


if __name__ == "__main__":
    main()
