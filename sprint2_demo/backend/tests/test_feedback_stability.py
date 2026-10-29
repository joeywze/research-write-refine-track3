"""Regression tests for unchanged-text scoring and accountable targeted edits."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.writing.critic import CriticError, QualitativeCritic, validate_critique, attach_critique
from src.writing.contracts import digest
from src.writing.demo import fixture_inputs
from src.writing.diagnostics import diagnose
from src.writing.pipeline import run_study
from src.writing.preservation import SemanticGate
from src.writing.demo import FixtureProvider
from src.writing.revision import review_points, apply_guided_edits
from src.writing.storage import RunStore
from test_critic import review, Scripted


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.package, self.original, self.approved = fixture_inputs()
        self.parent = Path(__file__).resolve().parents[1] / ".test-work"
        self.parent.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(dir=self.parent)
        self.addCleanup(self.temp.cleanup)
        self.store = RunStore(Path(self.temp.name) / "run")
        self.p = self.original.paragraphs[1]
        self.pid = self.p.paragraph_id
        self.allowed = (self.pid,)
        self.initial_raw = review(self.original, ((self.pid, "specificity"), ("p_abstract", "argument_strength")))
        self.initial = validate_critique(self.initial_raw, self.original)
        self.initial["package_hash"] = digest(self.package)
        self.initial["assessment_configuration"] = QualitativeCritic(Scripted([])).configuration()
        self.candidate = replace(self.original, paragraphs=tuple(
            replace(p, text=p.text.replace("The purpose is", "The aim is")) if p.paragraph_id == self.pid else p
            for p in self.original.paragraphs))
        self.points = review_points(attach_critique(diagnose(self.original), self.initial), self.allowed)

    def subset(self, raw):
        return {"paragraphs": [p for p in raw["paragraphs"] if p["paragraph_id"] == self.pid]}

    def response(self, points=None):
        return {"edits": [{"paragraph_id": self.pid,
                           "text": next(p.text for p in self.candidate.paragraphs if p.paragraph_id == self.pid)}],
                "review_responses": [{"finding_id": p["finding_id"], "decision": "EDITED",
                    "explanation": "Scripted attempt; the independent fixture critic decides the outcome.",
                    "before_quote": "The purpose is", "after_quote": "The aim is"}
                    for p in (self.points if points is None else points)]}

    def test_all_rules_and_actionable_llm_findings_receive_distinct_ids(self):
        self.assertTrue(any(p["method"] == "rules" for p in self.points))
        self.assertTrue(any(p["method"] == "llm" for p in self.points))
        self.assertEqual(len(self.points), len({p["finding_id"] for p in self.points}))
        self.assertTrue(all(p["paragraph_id"] == self.pid for p in self.points))

    def test_complete_trace_accepts_actual_quotes_but_does_not_claim_resolution(self):
        self.assertEqual(apply_guided_edits(self.original, self.response(), self.allowed, self.points), self.candidate)

    def test_missing_duplicate_and_unknown_responses_are_rejected(self):
        for mutation in ("missing", "duplicate", "unknown"):
            response = self.response()
            if mutation == "missing": response["review_responses"].pop()
            if mutation == "duplicate": response["review_responses"].append(deepcopy(response["review_responses"][0]))
            if mutation == "unknown": response["review_responses"][0]["finding_id"] = "invented"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                apply_guided_edits(self.original, response, self.allowed, self.points)

    def test_false_edit_claims_and_fabricated_quotes_are_rejected(self):
        for mutation in ("unchanged", "same_quote", "invented_before", "invented_after"):
            response = self.response()
            if mutation == "unchanged": response["edits"][0]["text"] = self.p.text
            if mutation == "same_quote": response["review_responses"][0]["after_quote"] = "The purpose is"
            if mutation == "invented_before": response["review_responses"][0]["before_quote"] = "invented wording"
            if mutation == "invented_after": response["review_responses"][0]["after_quote"] = "invented wording"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                apply_guided_edits(self.original, response, self.allowed, self.points)

    def test_no_safe_edit_can_leave_text_unchanged(self):
        response = {"edits": [], "review_responses": [{"finding_id": p["finding_id"], "decision": "NO_SAFE_EDIT",
                    "explanation": "The wording is necessary to preserve the planned study status.",
                    "before_quote": "", "after_quote": ""} for p in self.points]}
        self.assertEqual(apply_guided_edits(self.original, response, self.allowed, self.points), self.original)
        response["edits"] = self.response()["edits"]
        with self.assertRaisesRegex(ValueError, "changed paragraph"):
            apply_guided_edits(self.original, response, self.allowed, self.points)

    def test_changed_paragraphs_reassessed_and_unchanged_findings_retained(self):
        provider = Scripted([self.subset(review(self.candidate))])
        result = QualitativeCritic(provider).assess(self.package, self.candidate, "changed", self.store,
            previous_draft=self.original, previous_critique=self.initial)
        self.assertEqual(result["actionable_count"], 1)
        self.assertEqual(provider.calls[0][1]["paragraph_ids_to_assess"], [self.pid])
        self.assertEqual(len(provider.calls[0][1]["draft"]["paragraphs"]), len(self.original.paragraphs))
        initial_rows = {p["paragraph_id"]: p for p in self.initial["paragraphs"]}
        for row in result["paragraphs"]:
            if row["paragraph_id"] != self.pid:
                self.assertEqual(row, initial_rows[row["paragraph_id"]])
        self.assertEqual(provider.calls[0][1]["previous_assessment"]["paragraphs"], [initial_rows[self.pid]])

    def test_identical_draft_retains_counts_without_a_model_call(self):
        provider = Scripted([])
        result = QualitativeCritic(provider).assess(self.package, self.original, "same", self.store,
            previous_draft=self.original, previous_critique=self.initial)
        self.assertFalse(provider.calls)
        self.assertEqual(result["paragraphs"], self.initial["paragraphs"])
        self.assertFalse(result["assessment_scope"]["model_call_made"])

    def test_model_cannot_insert_findings_in_an_unrequested_unchanged_paragraph(self):
        provider = Scripted([review(self.candidate, (("p_abstract", "formulaic_language"),))])
        with self.assertRaises(CriticError):
            QualitativeCritic(provider).assess(self.package, self.candidate, "extra", self.store,
                previous_draft=self.original, previous_critique=self.initial)

    def test_missing_changed_paragraph_or_criterion_fails_closed(self):
        for index, response in enumerate(({"paragraphs": []}, self.subset(review(self.candidate)))):
            if index: response["paragraphs"][0]["findings"].pop()
            with self.subTest(index=index), self.assertRaises(CriticError):
                QualitativeCritic(Scripted([response])).assess(self.package, self.candidate, f"bad_{index}", self.store,
                    previous_draft=self.original, previous_critique=self.initial)

    def test_mismatched_cached_draft_package_or_version_never_reaches_model(self):
        for key in ("draft_hash", "package_hash", "version", "assessment_configuration"):
            bad = deepcopy(self.initial)
            bad[key] = "wrong"
            provider = Scripted([])
            with self.subTest(key=key), self.assertRaises(CriticError):
                QualitativeCritic(provider).assess(self.package, self.candidate, key, self.store,
                    previous_draft=self.original, previous_critique=bad)
            self.assertFalse(provider.calls)

    def test_new_or_unresolved_findings_in_changed_text_are_not_hidden(self):
        for index, criterion in enumerate(("specificity", "formulaic_language")):
            raw = self.subset(review(self.candidate, ((self.pid, criterion),)))
            result = QualitativeCritic(Scripted([raw])).assess(self.package, self.candidate, f"new_{index}", self.store,
                previous_draft=self.original, previous_critique=self.initial)
            self.assertEqual(result["actionable_count"], 2)

    def test_writer_claiming_success_does_not_override_unresolved_critic_finding(self):
        # Use the zero-rule draft so only the critic could justify acceptance.
        from src.writing.demo import remove_transitions
        original = replace(self.original, paragraphs=tuple(replace(p, text=remove_transitions(p.text)) for p in self.original.paragraphs))
        p = original.paragraphs[1]
        candidate = replace(original, paragraphs=tuple(replace(q, text=q.text.replace("The purpose is", "The aim is"))
                            if q.paragraph_id == p.paragraph_id else q for q in original.paragraphs))
        response = {"edits": [{"paragraph_id": p.paragraph_id, "text": candidate.paragraphs[1].text}],
                    "review_responses": [{"finding_id": "L:" + p.paragraph_id + ":specificity", "decision": "EDITED",
                    "explanation": "The scripted writer claims it fixed specificity.",
                    "before_quote": "The purpose is", "after_quote": "The aim is"}]}
        provider = Scripted([review(original, ((p.paragraph_id, "specificity"),)),
                             self.subset(review(candidate, ((p.paragraph_id, "specificity"),)))])
        gate = SemanticGate(FixtureProvider("fixture-auditor", [digest(original), digest(candidate)]))
        writer = Scripted([response], "fixture-writer")
        generic = Scripted([{"edits": []}], "fixture-writer")
        result = run_study(self.package, original, writer, gate, {"generic": (generic, gate), "guided": (writer, gate)},
            self.store, critic=QualitativeCritic(provider))
        self.assertEqual(result["results"]["guided"]["stop_reason"], "INSUFFICIENT_IMPROVEMENT")
        self.assertEqual(result["results"]["guided"]["final_hash"], digest(original))


if __name__ == "__main__":
    unittest.main()
