"""Half 2 pipeline: detector-guided rewriting with every content check in front of it.

    V0 + research package
      -> score every editable paragraph with the stylometric detector
      -> Guan Hong's context critic reviews the draft once and gives leads (always on; a failed
         review is retried once, then the run continues without notes)
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
  python half2_pipeline.py --plan [--topic cluster0]                # offline: which paragraphs would be revised
  python half2_pipeline.py --output runs/half2-<date> --writer-model <m1> --checker-model <m2> \
      [--critic-model <m3>] [--paragraphs P002,P027] [--max-paragraphs 4]
"""

import argparse
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

from handover import render
from project_io import read_input, validate_upload
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
DEFAULT_CRITIC = "gpt-5.6-luna"   # must differ from the writer and the checker
THRESHOLD = 35.0          # the target: stop once a safe rewrite scores at or below this
MIN_GAIN = 5.0            # a rewrite must lower the score by at least this much to count
CRITIC_RETRIES = 2        # the critic is asked up to three times
CRITIC_OUTPUT_TOKENS = 20_000  # whole-paper review; 6,000 was too few for 30-40 paragraphs
CRITIC_TIMEOUT = 300      # seconds per critic call
MIN_WORDS = 40

REWRITE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["paragraph"],
                  "properties": {"paragraph": {"type": "string"}}}


TOPIC_INDEX = HERE.parent / "drafts" / "track3_five_topic_index.json"


def load_topic(topic=None):
    """Load a topic as (package, v0, manifest, facts_file, label).

    topic=None   -> the reviewed example in sprint2_demo/inputs/converted (cluster7)
    topic="cluster0" -> looked up in drafts/track3_five_topic_index.json (Half 1's topic list)
    topic=<folder>   -> any folder holding research_package.json and v0.json (+ master_facts.xlsx)
    New topics are loaded like a website upload: the package and draft are validated and the page
    layout is generated from the draft, so nothing about a topic is hard-coded here."""
    if topic is None or str(topic) in ("cluster7", str(INPUTS)):
        package, v0, manifest = read_input(INPUTS)
        return package, v0, manifest, checks.FACTS_FILE, "cluster7"
    folder = Path(topic)
    if not folder.is_dir():
        if not TOPIC_INDEX.exists():
            raise ValueError(f"No folder {topic!r}, and no topic list at {TOPIC_INDEX}")
        entries = {t["id"]: t for t in json.loads(TOPIC_INDEX.read_text(encoding="utf-8"))["topics"]}
        if topic not in entries:
            raise ValueError(f"Unknown topic {topic!r}; choose from {', '.join(entries)}")
        entry = entries[topic]
        if entry["package"].startswith("sprint2_demo/inputs/converted"):
            return load_topic(None)
        folder = HERE.parent / Path(entry["package"]).parent
    package, v0, manifest = validate_upload((folder / "research_package.json").read_bytes(),
                                            (folder / "v0.json").read_bytes())
    facts = folder / "master_facts.xlsx"
    return package, v0, manifest, (facts if facts.exists() else checks.FACTS_FILE), folder.name if folder.name != "handover" else folder.parent.name


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


class CriticUnavailable(RuntimeError):
    """The critic could not review V0, so a live run stops before any rewriting (fail closed)."""


def review(critic, package, draft, label, store, retries=CRITIC_RETRIES):
    """Run Guan Hong's context critic; a failed review never stops the rewriting.

    Returns (critique or None, note). A failed or malformed answer is asked again (up to `retries`
    more times); the caller decides what happens if every try fails."""
    from src.writing.providers import BudgetExceeded
    errors = []
    for attempt in range(retries + 1):
        # Each try saves its files under its own name: the run store refuses to overwrite a file, so
        # reusing the label made every retry fail and hid the first error.
        name = label if attempt == 0 else f"{label}_retry{attempt}"
        try:
            return critic.assess(package, draft, name, store), "ok" if attempt == 0 else f"ok on retry {attempt}"
        except BudgetExceeded:
            raise
        except Exception as exc:  # malformed or failed review: ask again under a new name
            errors.append(f"try {attempt + 1}: {type(exc).__name__}: {exc}")
    return None, "unavailable (" + "; ".join(errors) + ")"


def needs_research(critique):
    """NEEDS_RESEARCH findings: problems the rewriter must not fix by itself (for Team A)."""
    out = []
    for row in (critique or {}).get("paragraphs", []):
        for f in row["findings"]:
            if f["status"] == "NEEDS_RESEARCH":
                out.append({"paragraph_id": row["paragraph_id"], "criterion": f["criterion"],
                            "explanation": f["explanation"]})
    return out


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
        extra.append(f"About your previous attempt: {last_rejection}.")
    extra.append('Keep [[S01]]-style citation tokens exactly. Return JSON: {"paragraph": "<revised paragraph>"}.')
    rules = rules.replace("Return only the revised paragraph.", "").strip()
    return rules + "\n\n" + "\n\n".join(extra)


def revise_paragraph(package, v0, current, pid, result, model, writer, *, evidence_gate, semantic_gate,
                     leads=(), attempts=MAX_ATTEMPTS, progress=None, target=THRESHOLD, min_gain=MIN_GAIN):
    """Up to `attempts` rewrites. A rewrite counts only if it lowers the score by at least `min_gain`
    AND passes every content check. A safe rewrite that still scores above `target` is kept as the
    best so far and handed back to the writer to improve further; the lowest-scoring safe version wins.
    Every attempt is checked against the ORIGINAL paragraph, so changes cannot drift step by step."""
    original = checks.paragraph(current, pid).text
    record = {"paragraph_id": pid, "section": checks.paragraph(v0, pid).section,
              "score_before": result["score"],
              "top_features": [rl.PLAIN_NAMES.get(k, k) for k, v in result["contributions"].items() if v > 0.1][:3],
              "critic_leads": list(leads), "attempts": [], "outcome": "kept original",
              "text_before": original, "text_after": original, "score_after": result["score"]}
    best_text, best_result = None, None
    last_note = ""
    for attempt in range(1, attempts + 1):
        base_text, base_result = (best_text, best_result) if best_text else (original, result)
        candidate, new_result = "", None
        try:
            response = writer.generate("half2_rewrite", instructions(base_result, leads, last_note),
                                       {"paragraph": base_text}, REWRITE_SCHEMA, 4000)
            candidate = str(response.get("paragraph", "")).strip()
        except Exception as error:  # a failed model call is a failed attempt, never a pass
            results = [checks.CheckResult("writer", "CHECK_ERROR", f"{type(error).__name__}: {error}")]
        else:
            new_result = score(candidate, model) if candidate else None
            needed = (best_result or result)["score"] - (min_gain if best_text is None else 0.5)
            if not candidate or candidate == original or candidate == best_text:
                results = [checks.CheckResult("writer", "NO_CHANGE", "the rewrite repeated an earlier version")]
            elif new_result["score"] > needed:
                # Checked before the model checks, so a rewrite that does not help costs no API call.
                results = [checks.CheckResult("detector", "NO_IMPROVEMENT",
                    f"score {new_result['score']:.0f} is not at least {min_gain:.0f} points below "
                    f"{result['score']:.0f}" if best_text is None else
                    f"score {new_result['score']:.0f} is not below the best safe version ({best_result['score']:.0f})")]
            else:
                results = checks.check_rewrite(package, v0, current, pid, candidate,
                                               evidence_gate=evidence_gate, semantic_gate=semantic_gate)
        safe = bool(results) and all(r.passed for r in results)
        new_score = new_result["score"] if new_result else None
        if safe:
            best_text, best_result = candidate, new_result
        done = safe and new_score <= target
        verdict = checks.summary(results)
        if safe and not done:
            verdict += f"; still scores {new_score:.0f} (target {target:.0f}), trying to lower it further"
        record["attempts"].append({"attempt": attempt, "text": candidate, "score": new_score,
                                   "accepted": safe, "checks": checks.as_dicts(results), "verdict": verdict})
        if progress:
            progress(pid, attempt, safe, verdict, new_score)
        if done:
            break
        if safe:
            last_note = (f"that version passed every content check but still scores {new_score:.0f}. "
                         "Make further changes to the signals listed above, keeping every fact, hedge and citation")
        elif results and results[0].status in ("NO_IMPROVEMENT", "NO_CHANGE"):
            last_note = (verdict.replace("rejected by ", "") + ". That attempt changed too little: punctuation, "
                         "single-word swaps and reordering a list do not move the score. This time change the sentence "
                         "structure itself where the signals above point: merge two sentences or split a long one, vary "
                         "where sentences start, cut a weak list item, and replace stock phrases with plain wording. "
                         "Keep every fact, number, hedge and citation, and keep every sentence complete")
        else:
            last_note = verdict.replace("rejected by ", "")
    if best_text:
        record.update(outcome="revised", text_after=best_text, score_after=best_result["score"])
        return record, checks.with_paragraph(current, pid, best_text)
    # Kept as written: the content is still correct, but a person should edit its style by hand.
    record["needs_human_edit"] = result["score"] >= target
    return record, current


def held_record(v0, pid, result, finding):
    text = checks.paragraph(v0, pid).text
    return {"paragraph_id": pid, "section": checks.paragraph(v0, pid).section, "score_before": result["score"],
            "top_features": [rl.PLAIN_NAMES.get(k, k) for k, v in result["contributions"].items() if v > 0.1][:3],
            "critic_leads": [], "attempts": [], "outcome": "held for research",
            "held_reason": f'{finding["criterion"]}: {finding["explanation"]}',
            "text_before": text, "text_after": text, "score_after": result["score"], "needs_human_edit": False}


def run(package, v0, manifest, model, writer, store, *, evidence_gate=None, semantic_gate=None, critic=None,
        threshold=THRESHOLD, only=None, limit=None, progress=None, topic="cluster7", require_critic=False):
    start = perf_counter()
    targets = select(v0, manifest, model, threshold, only, limit)
    leads, before, critic_status = {}, None, "not run"
    if critic is not None:
        before, critic_status = review(critic, package, v0, "v0_review", store)
        if before is None and require_critic:
            store.event("run_stopped", reason="critic unavailable", detail=critic_status)
            raise CriticUnavailable(f"The critic could not review V0, so nothing was rewritten: {critic_status}")
        leads = critic_leads(before)
    # Paragraphs the critic says need new research are not rewritten: a rewrite could hide the gap.
    held = {n["paragraph_id"]: n for n in needs_research(before)}
    current, records = v0, []
    for pid, result in targets:
        if pid in held:
            records.append(held_record(v0, pid, result, held[pid]))
            continue
        record, current = revise_paragraph(package, v0, current, pid, result, model, writer,
                                           evidence_gate=evidence_gate, semantic_gate=semantic_gate,
                                           leads=leads.get(pid, ()), progress=progress)
        records.append(record)
    after_leads, after_status = None, "not run"
    if critic is not None and current != v0:
        after, after_status = review(critic, package, current, "final_review", store)
        after_leads = critic_leads(after) if after is not None else None
    store.write("final_draft.json", current)
    (store.directory / "final_paper.md").write_text(render(current, manifest), encoding="utf-8")
    report = {
        "topic": topic,
        "interpretation": "The detector chose paragraphs and gave feedback; only the content checks could accept a rewrite.",
        "threshold": threshold,
        "paragraphs": records,
        "totals": {"selected": len(records),
                   "revised": sum(r["outcome"] == "revised" for r in records),
                   "kept_original": sum(r["outcome"] != "revised" for r in records),
                   "attempts": sum(len(r["attempts"]) for r in records),
                   "needs_human_edit": sum(bool(r.get("needs_human_edit")) for r in records),
                   "held_for_research": sum(r["outcome"] == "held for research" for r in records),
                   "mean_score_before": mean([r["score_before"] for r in records]),
                   "mean_score_after": mean([r["score_after"] for r in records])},
        "critic": None if critic is None else {
            "model": getattr(critic, "model", None),
            "review_of_v0": critic_status, "review_of_final": after_status,
            "actionable_before": sum(len(v) for v in leads.values()) if before is not None else None,
            "actionable_after": None if after_leads is None else sum(len(v) for v in after_leads.values()),
            "needs_research": needs_research(before)},
    }
    store.write("change_report.json", report)
    (store.directory / "change_report.md").write_text(as_markdown(report), encoding="utf-8")
    store.write("run_summary.json", {
        "topic": topic,
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
    lines = ["# Half 2 change report", "", f"Topic: {report.get('topic', 'cluster7')}", "",
             f"{t['revised']} of {t['selected']} selected paragraphs revised; {t['kept_original']} kept as written. "
             f"Mean detector score on selected paragraphs: {t['mean_score_before']} -> {t['mean_score_after']}.", "",
             f"Needs a human edit (kept as written, still at or above {report['threshold']:.0f}): "
             + (", ".join(r["paragraph_id"] for r in report["paragraphs"] if r.get("needs_human_edit")) or "none") + ".", "",
             "Held for research (the critic found a gap that needs new evidence, so not rewritten): "
             + (", ".join(r["paragraph_id"] for r in report["paragraphs"] if r["outcome"] == "held for research")
                or "none") + ".", "",
             "| Paragraph | Score | Outcome | Attempts | Last verdict |", "|---|---|---|---|---|"]
    for r in report["paragraphs"]:
        last = r["attempts"][-1]["verdict"] if r["attempts"] else ""
        lines.append(f"| {r['paragraph_id']} | {r['score_before']:.0f} -> {r['score_after']:.0f} | {r['outcome']} "
                     f"| {len(r['attempts'])} | {last} |")
    c = report.get("critic")
    if c:
        lines += ["", f"Reviewer ({c['model']}): V0 review {c['review_of_v0']}; final review {c['review_of_final']}. "
                      f"Actionable findings before -> after: {c['actionable_before']} -> {c['actionable_after']}."]
        if c["needs_research"]:
            lines += ["", "Needs research (for Team A; the rewriter does not change these):"]
            lines += [f"- {n['paragraph_id']} ({n['criterion']}): {n['explanation']}" for n in c["needs_research"]]
    for r in report["paragraphs"]:
        lines += ["", f"## {r['paragraph_id']} ({r['section'].replace('_', ' ')})", "",
                  f"Why selected: detector score {r['score_before']:.0f}; "
                  + (", ".join(r["top_features"]) or "no single dominant feature") + "."]
        if r["critic_leads"]:
            lines.append("Reviewer leads: " + " | ".join(r["critic_leads"]))
        if r.get("held_reason"):
            lines.append("Held for research: " + r["held_reason"])
        for a in r["attempts"]:
            lines.append(f"- Attempt {a['attempt']}: {a['verdict']}")
        lines += ["", f"**Before:** {checks.plain(r['text_before'])}", "",
                  f"**After:** {checks.plain(r['text_after'])}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", help="cluster7 (default), a topic id from drafts/track3_five_topic_index.json "
                                        "such as cluster0, or a folder with research_package.json and v0.json")
    parser.add_argument("--detector-model", type=Path, default=MODEL_FILE)
    parser.add_argument("--plan", action="store_true", help="offline: list the paragraphs that would be revised")
    parser.add_argument("--output", type=Path, help="new run directory")
    parser.add_argument("--writer-model")
    parser.add_argument("--checker-model", help="evidence and meaning checks (must differ from the writer)")
    parser.add_argument("--critic-model", default=DEFAULT_CRITIC,
                        help=f"Guan Hong's context critic, run before and after (default {DEFAULT_CRITIC})")
    parser.add_argument("--paragraphs", help="comma-separated IDs to revise, e.g. P002,P027 (demo / hard case)")
    parser.add_argument("--max-paragraphs", type=int)
    parser.add_argument("--threshold", type=float, default=THRESHOLD)
    parser.add_argument("--token-limit", type=int, default=1_500_000)
    args = parser.parse_args(argv)
    package, v0, manifest, facts_file, label = load_topic(args.topic)
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
    critic_model = (args.critic_model or "").strip()
    if not critic_model:
        parser.error("the critic is always on: give a --critic-model (default %s)" % DEFAULT_CRITIC)
    models = [m.strip().casefold() for m in (args.writer_model, args.checker_model, critic_model) if m]
    if len(models) != len(set(models)):
        parser.error("writer, checker and critic must be three different models")
    store = RunStore(args.output)
    budget = TokenBudget(args.token_limit)
    writer = OpenAIJSON(args.writer_model, budget, store, stage="writer")
    evidence_gate = checks.EvidenceGate(OpenAIJSON(args.checker_model, budget, store, stage="evidence"),
                                        checks.EvidenceIndex(package, facts_file).learn_authors(v0))
    semantic_gate = SemanticGate(OpenAIJSON(args.checker_model, budget, store, stage="preservation"))
    from src.writing.critic import QualitativeCritic
    from refine_accepted import detector_hints
    editable = editable_ids(manifest)
    # The critic reviews the whole paper in one answer: give it room to finish (6,000 output tokens cut it
    # off: "The model response did not complete") and time to write that much.
    critic = QualitativeCritic(OpenAIJSON(critic_model, budget, store, stage="critique", timeout=CRITIC_TIMEOUT),
                               max_output_tokens=CRITIC_OUTPUT_TOKENS,
                               detector_hints=lambda d: detector_hints(d, model, editable),
                               editable_ids=sorted(editable))

    def progress(pid, attempt, ok, verdict, new_score):
        print(f"{datetime.now():%H:%M:%S} {pid} attempt {attempt}: {'passed checks' if ok else 'rejected'} - {verdict}")

    try:
        report, _ = run(package, v0, manifest, model, writer, store, evidence_gate=evidence_gate,
                        semantic_gate=semantic_gate, critic=critic, threshold=args.threshold, only=only,
                        limit=args.max_paragraphs, progress=progress, topic=label, require_critic=True)
    except CriticUnavailable as error:
        raise SystemExit(f"STOPPED: {error}\nDetails are in {store.directory / 'events.jsonl'}") from None
    print(json.dumps(report["totals"], indent=2))
    final = report["critic"]["review_of_final"]
    if not final.startswith("ok") and final != "not run":
        print(f"WARNING: the critic reviewed V0 but not the final draft ({final}).")
    print(f"Saved final_paper.md and change_report.md to {store.directory}")


if __name__ == "__main__":
    main()
