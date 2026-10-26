"""Replay the failed real input with controlled judgements; not live quality evidence."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from handover import ROOT, Draft, read
from run_live import prepare
from citation_calibration import development_cases
from src.writing.contracts import digest
from src.writing.critic import QualitativeCritic, validate_critique, attach_critique, guided_improvement
from src.writing.diagnostics import diagnose
from src.writing.revision import review_points, apply_guided_edits
from src.writing.storage import RunStore
from src.writing.pipeline import run_study
from src.writing.preservation import SemanticGate
from test_citation_policy import RecordedVerdict


class ReplayedCaseTests(unittest.TestCase):
    def setUp(self):
        self.package, self.original, _ = prepare()
        prior = ROOT / "runs/live-20261025T142355415015Z"
        self.previous_candidate = Draft.from_dict(json.loads(read(prior / "guided_1_candidate.json")), self.package)
        self.initial = validate_critique(json.loads(read(prior / "v0_critic_response.json")), self.original)
        self.initial["package_hash"] = digest(self.package)
        self.parent = ROOT / ".test-work"
        self.parent.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(dir=self.parent)
        self.addCleanup(self.temp.cleanup)
        self.store = RunStore(Path(self.temp.name) / "review")
        self.allowed = ("P002", "P007", "P008")
        self.points = review_points(attach_critique(diagnose(self.original), self.initial), self.allowed)

    def test_previous_writer_response_without_feedback_coverage_is_rejected(self):
        edits = [{"paragraph_id": p.paragraph_id, "text": p.text} for p, old in
                 zip(self.previous_candidate.paragraphs, self.original.paragraphs) if p.text != old.text]
        with self.assertRaisesRegex(ValueError, "guided revision"):
            apply_guided_edits(self.original, {"edits": edits}, self.allowed, self.points)

    def test_safe_citation_move_can_be_explained_without_weakening_fixed_checks(self):
        safe = development_cases(self.package, self.original)[1]["candidate"]
        old = {p.paragraph_id: p.text for p in self.original.paragraphs}
        new = {p.paragraph_id: p.text for p in safe.paragraphs}
        response = {"edits": [{"paragraph_id": pid, "text": new[pid]} for pid in self.allowed],
                    "review_responses": [{"finding_id": f["finding_id"], "decision": "EDITED",
                    "explanation": "Move each citation beside the same study-specific claim; preserve its count and attribution.",
                    "before_quote": old[f["paragraph_id"]], "after_quote": new[f["paragraph_id"]]} for f in self.points]}
        self.assertEqual(apply_guided_edits(self.original, response, self.allowed, self.points), safe)

    def test_failed_candidate_keeps_three_unresolved_findings_under_controlled_critic(self):
        texts = {p.paragraph_id: p.text for p in self.previous_candidate.paragraphs}
        partial = {"paragraphs": [deepcopy(p) for p in self.initial["paragraphs"] if p["paragraph_id"] in {"P002", "P007"}]}
        for row in partial["paragraphs"]:
            for finding in row["findings"]:
                if finding["status"] == "ACTIONABLE":
                    finding["quote"] = texts[row["paragraph_id"]]
                    finding["explanation"] = "Controlled regression verdict: the citation moves were not made."

        class ControlledCritic:
            model = "offline-regression-critic"
            test_only = True

            def generate(self, task, instructions, payload, schema, cap):
                if payload["paragraph_ids_to_assess"] != ["P002", "P007"]:
                    raise AssertionError("Unexpected reassessment scope")
                return partial

        self.initial["assessment_configuration"] = QualitativeCritic(ControlledCritic()).configuration()
        after = QualitativeCritic(ControlledCritic()).assess(self.package, self.previous_candidate, "replay", self.store,
            previous_draft=self.original, previous_critique=self.initial)
        self.assertEqual(after["actionable_count"], 3)
        self.assertEqual(len(after["assessment_scope"]["retained_paragraph_ids"]), 37)
        self.assertIn("P008", after["assessment_scope"]["retained_paragraph_ids"])
        rows = {p["paragraph_id"]: p for p in after["paragraphs"]}
        for pid in ("P001", "P006", "P039"):
            self.assertFalse(any(f["status"] == "ACTIONABLE" for f in rows[pid]["findings"]))
        self.assertFalse(guided_improvement(attach_critique(diagnose(self.original), self.initial),
                                           attach_critique(diagnose(self.previous_candidate), after), 1))

    def test_feedback_accounting_does_not_override_a_semantic_rejection(self):
        bad = development_cases(self.package, self.original)[3]["candidate"]
        original = {p.paragraph_id: p.text for p in self.original.paragraphs}
        wrong = {p.paragraph_id: p.text for p in bad.paragraphs}
        response = {"edits": [{"paragraph_id": "P002", "text": wrong["P002"]}], "review_responses": []}
        for point in self.points:
            changed = point["paragraph_id"] == "P002"
            response["review_responses"].append({"finding_id": point["finding_id"],
                "decision": "EDITED" if changed else "NO_SAFE_EDIT",
                "explanation": "Controlled writer response; its citation-move claim must not decide preservation.",
                "before_quote": original["P002"] if changed else "", "after_quote": wrong["P002"] if changed else ""})

        class Writer:
            model = "controlled-writer"
            test_only = True

            def generate(self, task, instructions, payload, schema, cap):
                return {"edits": []} if task == "revision_generic" else response

        class Checker:
            model = "controlled-checker"
            test_only = True

            def generate(self, task, instructions, payload, schema, cap):
                return (RecordedVerdict(self.original).response if payload["candidate_hash"] == digest(self.original)
                        else RecordedVerdict(bad, "P002", "CITATION_MISMATCH").response)

        # Bind the fixture input without putting it in any model prompt.
        checker = Checker()
        checker.original = self.original

        class CriticProvider:
            model = "controlled-critic"
            test_only = True

            def __init__(self, raw): self.raw, self.calls = raw, 0

            def generate(self, task, instructions, payload, schema, cap):
                self.calls += 1
                if self.calls > 1: raise AssertionError("A failed preservation check must stop critic reassessment")
                return self.raw

        raw = {"paragraphs": deepcopy(self.initial["paragraphs"])}
        critic = CriticProvider(raw)
        writer, gate = Writer(), SemanticGate(checker)
        result = run_study(self.package, self.original, writer, gate,
            {"generic": (writer, gate), "guided": (writer, gate)}, self.store, critic=QualitativeCritic(critic))
        final = result["results"]["guided"]
        self.assertEqual(final["stop_reason"], "PRESERVATION_FAILED")
        self.assertEqual(final["final_hash"], digest(self.original))
        self.assertEqual(critic.calls, 1)


if __name__ == "__main__":
    unittest.main()
