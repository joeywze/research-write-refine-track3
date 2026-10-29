"""Fixed development cases for the citation-policy repair, not a held-out evaluation."""
from dataclasses import asdict, replace
import json

from handover import ROOT, Draft, read
from src.writing.contracts import digest
from src.writing.preservation import SemanticGate, deterministic

VERSION = "citation-policy-v1-development-cases"
FROZEN_RUN = "live-20261025T083033779648Z"


def edited(draft, replacements):
    return replace(draft, paragraphs=tuple(replace(p, text=replacements[p.paragraph_id])
                   if p.paragraph_id in replacements else p for p in draft.paragraphs))


def development_cases(package, original):
    prior_path = ROOT / "runs" / FROZEN_RUN / "guided_1_candidate.json"
    prior = Draft.from_dict(json.loads(read(prior_path)), package)
    before = {p.paragraph_id: p.text for p in original.paragraphs}
    previous = {p.paragraph_id: p.text for p in prior.paragraphs}
    citation_only = edited(original, {pid: previous[pid] for pid in ("P002", "P007", "P008")})
    paraphrase = before["P001"].replace("describe different aspects", "capture different aspects")
    certainty = before["P006"].replace("remains unconfirmed", "is established")
    if paraphrase == before["P001"] or certainty == before["P006"]:
        raise ValueError("The frozen development text has changed; review the cases before running them")
    swapped = previous["P002"].replace("[[S01]]", "@@first@@").replace("[[S02]]", "[[S01]]").replace("@@first@@", "[[S02]]")
    return [
        {"id": "unchanged", "candidate": original, "expected_statuses": ["PASS"], "failure_paragraph": None,
         "rationale": "Identical text should not acquire a new edit-related citation or punctuation error."},
        {"id": "citation_moves", "candidate": citation_only, "expected_statuses": ["PASS"], "failure_paragraph": None,
         "rationale": "Only the three citation placements change. Each source remains beside the same named study claim; proposal wording stays unchanged."},
        {"id": "safe_paraphrase", "candidate": edited(original, {"P001": paraphrase}), "expected_statuses": ["PASS"], "failure_paragraph": None,
         "rationale": "Replacing 'describe different aspects' with 'capture different aspects' preserves the distinction being stated."},
        {"id": "swapped_attribution", "candidate": edited(original, {"P002": swapped}),
         "expected_statuses": ["CITATION_MISMATCH"], "failure_paragraph": "P002",
         "rationale": "The Fu/Liu and Chung clauses receive each other's source IDs. Counts are unchanged, but source attribution is wrong."},
        {"id": "overstated_certainty", "candidate": edited(original, {"P006": certainty}),
         "expected_statuses": ["MAJOR_DRIFT", "UNSUPPORTED_ADDITION"], "failure_paragraph": "P006",
         "rationale": "An unconfirmed research gap is described as established, removing an explicit uncertainty qualification."},
    ]


def matches_expectation(case, result):
    if result.status not in case["expected_statuses"]:
        return False
    if case["failure_paragraph"] is None:
        return result.status == "PASS"
    # A refusal, parse error or unrelated table failure is not correct detection.
    paragraphs = (result.semantic or {}).get("paragraphs", [])
    return any(p["paragraph_id"] == case["failure_paragraph"] and
               p["status"] in case["expected_statuses"] for p in paragraphs)


def run_calibration(package, original, provider_factory, store):
    cases = development_cases(package, original)
    report = {"version": VERSION, "status": "IN_PROGRESS", "original_hash": digest(original),
              "case_origin": FROZEN_RUN, "independent_human_labels": False, "held_out": False,
              "interpretation": "Agent-reviewed development expectations. These cases test this repair; they do not estimate general preservation accuracy.",
              "cases": []}
    store.write("calibration_cases.json", [dict(c, candidate=asdict(c["candidate"]),
                 candidate_hash=digest(c["candidate"])) for c in cases])
    for case in cases:
        candidate = case["candidate"]
        references = (original, original)
        basic = deterministic(package, candidate, references)
        if basic.status != "PASS":
            raise ValueError("A semantic calibration case unexpectedly failed the fixed-content check: " + case["id"])
        print("Checking development case: " + case["id"], flush=True)
        provider = provider_factory("calibration_" + case["id"])
        result = SemanticGate(provider, max_output_tokens=16000).check(package, candidate, references)
        row = {"id": case["id"], "candidate_hash": digest(candidate),
               "expected_statuses": case["expected_statuses"], "expected_failure_paragraph": case["failure_paragraph"],
               "deterministic_status": basic.status, "result": asdict(result),
               "matches_development_expectation": matches_expectation(case, result)}
        report["cases"].append(row)
        store.write("calibration_" + case["id"] + "_result.json", row)
        print("Development case " + case["id"] + ": " + result.status +
              (" (expected decision)" if row["matches_development_expectation"] else " (unexpected decision)"), flush=True)
        if result.status == "CHECK_ERROR":
            break  # Do not repeat paid calls after a transport or response-format failure.
    report["status"] = "PASS" if len(report["cases"]) == len(cases) and all(
        r["matches_development_expectation"] for r in report["cases"]) else "FAIL"
    store.write("calibration_summary.json", report)
    return report
