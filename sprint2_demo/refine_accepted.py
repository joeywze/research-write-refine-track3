"""Pilot one detector-assisted review and revision from a saved guided draft."""

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

from handover import Draft, LockedTablesGate, render
from project_io import read_input
from src.writing.contracts import digest
from src.writing.critic import QualitativeCritic, attach_critique
from src.writing.diagnostics import diagnose
from src.writing.evaluation import read_json
from src.writing.pipeline import RunConfig, require_independent, run_arm
from src.writing.preservation import SemanticGate, deterministic
from src.writing.providers import OpenAIJSON, TokenBudget
from src.writing.storage import RunStore

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from detection.detector import MODEL_FILE, score


def accepted_inputs(run, inputs):
    package, v0, manifest = read_input(inputs)
    v2 = Draft.from_dict(read_json(run / "guided_final.json"), package)
    study = read_json(run / "study_summary.json")
    guided = study["results"]["guided"]
    if (study["status"] != "COMPLETED" or study["package_hash"] != digest(package)
            or study["v0_hash"] != digest(v0) or guided["final_hash"] != digest(v2)):
        raise ValueError("The saved guided run does not match its draft or research inputs")
    if read_json(run / "v0_preservation.json")["status"] != "PASS":
        raise ValueError("The original draft did not pass preservation")
    attempts = guided["attempts"]
    if not isinstance(attempts, list) or len(attempts) > 3:
        raise ValueError("The saved run has an invalid guided attempt count")
    parent_hash = digest(v0)
    for index, attempt in enumerate(attempts, 1):
        if attempt["attempt"] != index or attempt["parent_hash"] != parent_hash:
            raise ValueError("The saved guided attempts do not form a single draft history")
        if attempt["accepted"]:
            checkpoint = Draft.from_dict(read_json(run / f"guided_{index}_accepted.json"), package)
            parent_hash = digest(checkpoint)
            verdict = read_json(run / f"guided_{index}_preservation.json")
            if verdict["status"] != "PASS" or parent_hash != attempt["candidate_hash"]:
                raise ValueError("A saved accepted revision has no matching preservation pass")
    if parent_hash != digest(v2):
        raise ValueError("V2 is not the last accepted guided draft")
    if deterministic(package, v2, (v0,)).status != "PASS":
        raise ValueError("V2 failed the local structure and content checks")
    original = {p.paragraph_id: p.text for p in v0.paragraphs}
    editable = {b["paragraph_id"] for b in manifest["blocks"] if b["kind"] == "prose" and not b["locked"]}
    if any(p.paragraph_id not in editable and p.text != original[p.paragraph_id] for p in v2.paragraphs):
        raise ValueError("A protected table or non-prose block changed in V2")
    render(v2, manifest)
    return package, v0, v2, manifest, editable, len(attempts)


def detector_scores(draft, model, editable, cohort=None):
    results = {}
    for paragraph in draft.paragraphs:
        pid = paragraph.paragraph_id
        if pid not in editable or (cohort is not None and pid not in cohort):
            continue
        result = score(paragraph.text, model)
        if cohort is not None or result["n_words"] >= 40:
            results[pid] = result
    return results


def detector_hints(draft, model, editable):
    scores = detector_scores(draft, model, editable)
    paragraphs = {p.paragraph_id: p for p in draft.paragraphs}
    shortlist = sorted(scores, key=lambda pid: scores[pid]["score"], reverse=True)[:8]
    hints = []
    for pid in shortlist:
        result = scores[pid]
        features = [key for key, value in result["contributions"].items() if value > 0][:3]
        passages = [f for f in result["flagged"] if f["sentence"] in paragraphs[pid].text][:2]
        if features or passages:
            hints.append({"paragraph_id": pid, "features_to_review": features, "matched_passages": passages})
    return hints


def refine_accepted(inputs, model, writer, checker, reviewer, store, *, writer_cap, review_cap):
    package, v0, v2, manifest, editable, prior_attempts = inputs
    if prior_attempts >= 3:
        raise ValueError("The saved draft has already used all three revision attempts")
    gate = LockedTablesGate(SemanticGate(checker, max_output_tokens=review_cap), manifest)
    critic = QualitativeCritic(reviewer, max_output_tokens=review_cap,
                              detector_hints=lambda draft: detector_hints(draft, model, editable),
                              editable_ids=sorted(editable))
    require_independent(writer, gate)
    require_independent(writer, critic)
    start = perf_counter()
    baseline_scores = detector_scores(v2, model, editable)
    store.write("accepted_v2.json", v2)
    (store.directory / "accepted_v2.md").write_text(render(v2, manifest), encoding="utf-8")
    store.write("refinement_configuration.json", {"detector_model_hash": digest(model),
                "v0_hash": digest(v0), "accepted_v2_hash": digest(v2), "package_hash": digest(package),
                "critic": critic.configuration(), "earlier_guided_attempts": prior_attempts,
                "maximum_additional_attempts": 1, "editable_paragraph_ids": sorted(editable)})
    critique = critic.assess(package, v2, "accepted_v2", store)
    report = attach_critique(diagnose(v2), critique)
    targets = tuple(p["paragraph_id"] for p in critique["paragraphs"]
                    if any(f["status"] == "ACTIONABLE" for f in p["findings"]))
    result = run_arm(package, v0, writer, gate, store, "guided",
                     RunConfig(max_attempts=1, max_output_tokens=writer_cap), targets,
                     initial_report=report, critic=critic, starting_draft=v2)
    final = Draft.from_dict(read_json(store.directory / "guided_final.json"), package)
    (store.directory / "guided_final_with_layout.md").write_text(render(final, manifest), encoding="utf-8")
    final_scores = detector_scores(final, model, editable, cohort=baseline_scores)
    store.write("detector_comparison.json", {
        "interpretation": "Descriptive detector scores on the same paragraphs. The score does not decide acceptance.",
        "paragraphs": [{"paragraph_id": pid, "accepted_v2": before["score"], "after_pass": final_scores[pid]["score"]}
                       for pid, before in baseline_scores.items()],
    })
    events = store.directory / "events.jsonl"
    calls = []
    if events.exists():
        for line in events.read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if event["kind"] == "model_call":
                calls.append(event)
    known = [event["usage"] for event in calls if event["usage"] is not None]
    summary = {"stop_reason": result["stop_reason"], "accepted_edit": digest(final) != digest(v2),
               "guided_attempts_including_this_pass": prior_attempts + len(result["attempts"]),
               "model_calls": len(calls), "usage_unknown_calls": len(calls) - len(known),
               "reported_input_tokens": sum(usage["input_tokens"] for usage in known) if known else None,
               "reported_output_tokens": sum(usage["output_tokens"] for usage in known) if known else None,
               "elapsed_seconds": perf_counter() - start, "test_only": writer.test_only}
    store.write("refinement_summary.json", summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="Completed Stage B run")
    parser.add_argument("--inputs", type=Path, required=True, help="Matching converted or uploaded input folder")
    parser.add_argument("--detector-model", type=Path, default=MODEL_FILE)
    parser.add_argument("--plan", action="store_true", help="Check the saved run and preview detector hints offline")
    parser.add_argument("--output", type=Path, help="New output directory for a live pass")
    parser.add_argument("--writer-model")
    parser.add_argument("--checker-model")
    parser.add_argument("--critic-model", help="Defaults to the checker model in a separate review call")
    parser.add_argument("--token-limit", type=int, default=1_000_000, help="Shared allowance for the optional pass")
    parser.add_argument("--writer-output-cap", type=int, default=16_000)
    parser.add_argument("--review-output-cap", type=int, default=32_000)
    args = parser.parse_args(argv)
    try:
        prepared = accepted_inputs(args.run, args.inputs)
        model = read_json(args.detector_model)
        if not isinstance(model, dict) or not model.get("features"):
            raise ValueError("The detector model must contain fitted features")
        _, _, v2, _, editable, used = prepared
        if args.plan:
            result = {"accepted_v2_hash": digest(v2), "earlier_guided_attempts": used,
                      "additional_attempt_available": used < 3, "detector_model_hash": digest(model),
                      "editable_paragraph_count": len(editable), "detector_hints": detector_hints(v2, model, editable)}
        else:
            if not args.output or not args.writer_model or not args.checker_model:
                parser.error("A live pass requires --output, --writer-model and --checker-model")
            if used >= 3:
                raise ValueError("The saved draft has already used all three revision attempts")
            if min(args.writer_output_cap, args.review_output_cap) < 1:
                raise ValueError("Output caps must be positive")
            critic_model = args.critic_model or args.checker_model
            writer_id, checker_id, critic_id = (name.strip().casefold() for name in
                                                (args.writer_model, args.checker_model, critic_model))
            if not all((writer_id, checker_id, critic_id)) or writer_id in (checker_id, critic_id):
                raise ValueError("Use a different model for writing and for each check of its output")
            budget = TokenBudget(args.token_limit)
            store = RunStore(args.output)
            writer = OpenAIJSON(args.writer_model, budget, store, stage="writer")
            checker = OpenAIJSON(args.checker_model, budget, store, stage="preservation")
            reviewer = OpenAIJSON(critic_model, budget, store, stage="critique")
            result = refine_accepted(prepared, model, writer, checker, reviewer, store,
                                     writer_cap=args.writer_output_cap, review_cap=args.review_output_cap)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
        parser.exit(1, f"{type(error).__name__}: {error}\n")


if __name__ == "__main__":
    main()
