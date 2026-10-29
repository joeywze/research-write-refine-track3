"""Export review materials and run a separate model check of preservation."""

from dataclasses import asdict
import csv
import json
from pathlib import Path
import random

from .contracts import Draft, ResearchPackage, digest
from .preservation import SemanticGate
from .providers import OpenAIJSON, TokenBudget
from .storage import RunStore


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def versions(directory):
    """Collect readable candidates, including rejected ones, from a saved run."""
    directory = Path(directory)
    package = ResearchPackage.from_dict(read_json(directory / "package.json"))
    v0 = Draft.from_dict(read_json(directory / "v0_accepted.json"), package)
    output = [("V0", v0)]
    for arm in ("generic", "guided"):
        for index in range(1, 4):
            path = directory / f"{arm}_{index}_candidate.json"
            if path.exists():
                try:
                    output.append((f"{arm}_{index}", Draft.from_dict(read_json(path), package)))
                except (ValueError, TypeError, KeyError):
                    pass  # Invalid candidates remain recorded in the run and manifest.
    return package, v0, output


def export_human(run_directories, output: Path, seed: int = 42):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    raters = output / "raters"
    private = output / "private"
    raters.mkdir()
    private.mkdir()
    cases, seen_packages, manifest = [], set(), []
    for index, directory in enumerate(run_directories, 1):
        package, v0, candidates = versions(directory)
        if package.package_id in seen_packages:
            raise ValueError("Use one run per package; its versions belong to the same case")
        seen_packages.add(package.package_id)
        grouped = {}
        for condition, candidate in candidates:
            grouped.setdefault(digest(candidate), {"draft": candidate, "conditions": []})["conditions"].append(condition)
        summary = read_json(Path(directory) / "study_summary.json")
        exported_conditions = {condition for condition, _ in candidates}
        manifest.append({"run": str(Path(directory).resolve()), "package_id": package.package_id,
                         "study_summary": summary,
                         "attempts_without_parseable_candidate": [
                             {"arm": arm, "attempt": attempt["attempt"], "reason": attempt["reason"]}
                             for arm, result in summary["results"].items() for attempt in result["attempts"]
                             if f"{arm}_{attempt['attempt']}" not in exported_conditions]})
        for draft_hash, item in grouped.items():
            cases.append({"case_id": f"case_{index}", "package": package, "v0": v0,
                          "draft": item["draft"], "conditions": item["conditions"],
                          "draft_hash": draft_hash, "run": str(Path(directory).resolve()),
                          "test_only": summary["test_only"]})
    random.Random(seed).shuffle(cases)
    key, items, source_items = [], [], []
    for index, item in enumerate(cases, 1):
        item_id = f"item_{index:04d}"
        key.append({"item_id": item_id, "case_id": item["case_id"], "conditions": item["conditions"],
                    "run": item["run"], "draft_hash": item["draft_hash"], "test_only": item["test_only"]})
        items.append({"item_id": item_id, "case_id": item["case_id"],
                      "text": item["draft"].markdown(item["package"])})
        source_items.append({"item_id": item_id, "package": asdict(item["package"]),
                             "protected_v0": asdict(item["v0"]), "candidate": asdict(item["draft"])})
    for path, records in ((raters / "writing_items.jsonl", items),
                          (raters / "preservation_evidence.jsonl", source_items),
                          (private / "condition_key.jsonl", key)):
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    (private / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    columns = ["rater_id", "item_id", "case_id", "clarity", "coherence", "naturalness", "technical_precision",
               "preservation_status", "evidence_comment"]
    with (raters / "ratings.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({"item_id": i["item_id"], "case_id": i["case_id"]} for i in items)
    (raters / "instructions.md").write_text(
        "# Review instructions\n\nFirst rate the candidate texts without opening the preservation "
        "evidence or condition key. Work independently and record a rater ID. Use 1 (poor), "
        "2 (weak), 3 (adequate), 4 (good) or 5 (excellent) for clarity, coherence, naturalness "
        "and technical precision. Naturalness means fluent academic prose. Leave a score "
        "blank if you cannot assess it, and explain why. Agree examples for each criterion "
        "on separate practice cases before starting.\n\n"
        "Submit the writing ratings before reviewing preservation. Then use V0 and the source "
        "evidence to check each candidate. Record PASS, MAJOR_DRIFT, UNSUPPORTED_ADDITION, "
        "CITATION_MISMATCH or UNCERTAIN, with the affected claim or paragraph and a reason. "
        "Check scope, polarity, qualifications, attribution and whether planned work has become "
        "a claimed result. Matching citations alone cannot establish unchanged meaning. "
        "Keep diagnostic scores and the condition key hidden throughout. "
        "Synthetic examples are for practice only.\n",
        encoding="utf-8")
    (private / "analysis_plan.md").write_text(
        "# Analysis plan\n\nKeep the condition key private. Distribute writing texts first and "
        "release preservation evidence after writing ratings are submitted, or use separate reviewer "
        "groups. Where feasible, collect independent ratings from at least two people.\n\n"
        "Compare the final accepted guided draft (V2) with the final generic draft (V1), "
        "including their token usage and latency. Also report change from V0. Compare first "
        "attempts separately to assess feedback on the shared paragraph targets. The generic "
        "writer receives no feedback. Later guided attempts involve extra calls.\n\n"
        "Report failed preservation checks and invalid attempts across all attempts, using "
        "events.jsonl and the saved summaries. The export includes readable rejected candidates "
        "and combines identical versions into one item. Keep missing outputs in the failure counts. "
        "Keep all sections and versions of a paper in one data partition. Compare ratings within "
        "paper and report reviewer disagreement. Freeze diagnostics before held-out evaluation. "
        "Internal issue counts show what the loop optimises; use independent assessment to "
        "judge whether the changes improve writing.\n", encoding="utf-8")
    return {"items": len(items), "cases": len(seen_packages), "seed": seed}


def held_out_audit(directory: Path, output: Path, model: str, token_limit=200_000, client=None):
    directory = Path(directory)
    configuration = read_json(directory / "configuration.json")
    if configuration["test_only"]:
        raise ValueError("The separate model audit needs a live run, not a scripted example")
    in_loop = [configuration["writer_model"], configuration["preservation_model"],
               configuration.get("critic_model")]
    if model.casefold().strip() in {m.casefold().strip() for m in in_loop if m}:
        raise ValueError("Choose an evaluator different from the writer, checker and optional style critic")
    store = RunStore(output)
    provider = OpenAIJSON(model, TokenBudget(token_limit), store, client=client)
    gate = SemanticGate(provider)
    package, v0, candidates = versions(directory)
    store.write("evaluation_configuration.json", {"source_run": str(directory.resolve()),
                                                 "package_hash": digest(package), "model": model,
                                                 "token_limit": token_limit})
    results = []
    for condition, candidate in candidates:
        # Supply the package and drafts without scores or acceptance decisions.
        report = gate.check(package, candidate, () if condition == "V0" else (v0,))
        record = {"condition": condition, "candidate_hash": digest(candidate), "report": asdict(report)}
        store.write(condition + "_audit.json", record)
        results.append(record)
    store.write("held_out_summary.json", {"results": results, "human_evaluation": "PENDING"})
    return results
