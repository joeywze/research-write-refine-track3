"""Control-flow regressions; fixture verdicts are not model-accuracy evidence."""
from dataclasses import asdict, replace
import json
import unittest

from handover import ROOT, Draft, ResearchPackage, read
from src.writing.contracts import digest
from src.writing.preservation import SemanticGate, deterministic, reference_comparisons


class RecordedVerdict:
    model = "offline-verdict-fixture"
    test_only = True

    def __init__(self, draft, failure_pid=None, status="PASS"):
        self.calls = []
        self.response = {"global_status": status, "global_reasons": [] if status == "PASS" else ["Controlled fixture verdict"],
            "paragraphs": [{"paragraph_id": p.paragraph_id, "checked_claim_ids": list(p.claim_ids),
                            "status": status if p.paragraph_id == failure_pid else "PASS",
                            "reasons": ["Controlled fixture verdict"] if p.paragraph_id == failure_pid else []}
                           for p in draft.paragraphs]}

    def generate(self, task, instructions, payload, schema, cap):
        self.calls.append({"instructions": instructions, "payload": payload})
        return self.response


def source_inputs():
    base = ROOT / "inputs/converted"
    package = ResearchPackage.from_dict(json.loads(read(base / "research_package.json")))
    original = Draft.from_dict(json.loads(read(base / "v0.json")), package)
    return package, original


def change(draft, pid, text):
    return replace(draft, paragraphs=tuple(replace(p, text=text) if p.paragraph_id == pid else p
                                          for p in draft.paragraphs))


class CitationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package, cls.original = source_inputs()
        frozen = ROOT / "runs/live-20261025T083033779648Z/guided_1_candidate.json"
        cls.previous_candidate = Draft.from_dict(json.loads(read(frozen)), cls.package)

    def test_exact_metadata_identifies_unchanged_table_in_failed_case(self):
        report = reference_comparisons(self.previous_candidate, (self.original,))[0]
        self.assertEqual(report["changed_paragraph_ids"], ["P001", "P002", "P006", "P007", "P008", "P039"])
        self.assertIn("P010", report["unchanged_paragraph_ids"])
        self.assertEqual(len(report["unchanged_paragraph_ids"]), 33)

    def test_comparison_keeps_both_v0_and_last_accepted_context(self):
        rows = reference_comparisons(self.previous_candidate, (self.original, self.previous_candidate))
        self.assertTrue(rows[0]["changed_paragraph_ids"])
        self.assertEqual(rows[1]["changed_paragraph_ids"], [])
        self.assertEqual(rows[1]["unchanged_paragraph_ids"], [p.paragraph_id for p in self.original.paragraphs])

    def test_safe_relocation_still_requires_model_approval(self):
        candidate = change(self.original, "P002", next(p.text for p in self.previous_candidate.paragraphs if p.paragraph_id == "P002"))
        self.assertEqual(deterministic(self.package, candidate, (self.original,)).status, "PASS")
        provider = RecordedVerdict(candidate)
        self.assertEqual(SemanticGate(provider).check(self.package, candidate, (self.original,)).status, "PASS")
        self.assertEqual(len(provider.calls), 1)
        context = provider.calls[0]["payload"]["reference_comparisons"][0]
        self.assertEqual(context["changed_paragraph_ids"], ["P002"])
        self.assertEqual(context["citation_sequences_in_changed_paragraphs"][0]["before"], ["S01", "S02"])
        self.assertEqual(context["citation_sequences_in_changed_paragraphs"][0]["after"], ["S01", "S02"])

    def test_swapped_attribution_with_same_counts_is_not_automatically_accepted(self):
        text = next(p.text for p in self.previous_candidate.paragraphs if p.paragraph_id == "P002")
        text = text.replace("[[S01]]", "@@first@@").replace("[[S02]]", "[[S01]]").replace("@@first@@", "[[S02]]")
        candidate = change(self.original, "P002", text)
        self.assertEqual(deterministic(self.package, candidate, (self.original,)).status, "PASS")
        provider = RecordedVerdict(candidate, "P002", "CITATION_MISMATCH")
        self.assertEqual(SemanticGate(provider).check(self.package, candidate, (self.original,)).status, "CITATION_MISMATCH")
        self.assertEqual(len(provider.calls), 1)

    def test_removed_source_is_rejected_before_model_call(self):
        p = next(p for p in self.original.paragraphs if p.paragraph_id == "P002")
        candidate = change(self.original, p.paragraph_id, p.text.replace("[[S01]]", ""))
        provider = RecordedVerdict(candidate)
        self.assertEqual(SemanticGate(provider).check(self.package, candidate, (self.original,)).status, "CITATION_MISMATCH")
        self.assertEqual(provider.calls, [])

    def test_changed_certainty_is_still_rejected_by_model_verdict(self):
        p = next(p for p in self.original.paragraphs if p.paragraph_id == "P006")
        candidate = change(self.original, p.paragraph_id, p.text.replace("remains unconfirmed", "is established"))
        self.assertNotEqual(digest(candidate), digest(self.original))
        self.assertEqual(deterministic(self.package, candidate, (self.original,)).status, "PASS")
        provider = RecordedVerdict(candidate, "P006", "MAJOR_DRIFT")
        self.assertEqual(SemanticGate(provider).check(self.package, candidate, (self.original,)).status, "MAJOR_DRIFT")

    def test_exact_metadata_does_not_silently_override_an_unchanged_block_failure(self):
        provider = RecordedVerdict(self.original, "P010", "CITATION_MISMATCH")
        result = SemanticGate(provider).check(self.package, self.original, (self.original,))
        self.assertEqual(result.status, "CITATION_MISMATCH")
        self.assertIn("P010", provider.calls[0]["payload"]["reference_comparisons"][0]["unchanged_paragraph_ids"])

    def test_reference_generator_is_retained_for_the_model_payload(self):
        provider = RecordedVerdict(self.original)
        result = SemanticGate(provider).check(self.package, self.original, (d for d in [self.original]))
        self.assertEqual(result.status, "PASS")
        self.assertEqual(len(provider.calls[0]["payload"]["references"]), 1)
        self.assertEqual(len(provider.calls[0]["payload"]["reference_comparisons"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
