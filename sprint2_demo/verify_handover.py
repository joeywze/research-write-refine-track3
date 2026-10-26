"""Offline handover checks. No model judgement or model-performance claim."""
from collections import Counter
from dataclasses import asdict, replace
import json
import unittest

from handover import ROOT, Draft, ResearchPackage, LockedTablesGate, build, read, render, write_json
from src.writing.contracts import CitationError
from src.writing.diagnostics import diagnose
from src.writing.preservation import deterministic, SemanticGate


class NoModel:
    model = "not-configured"
    test_only = True

    def generate(self, *args):
        raise RuntimeError("Semantic checks are not performed in offline verification")


class HandoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = build()
        converted = ROOT / "inputs/converted"
        cls.package = ResearchPackage.from_dict(json.loads(read(converted / "research_package.json")))
        cls.draft = Draft.from_dict(json.loads(read(converted / "v0.json")), cls.package)
        cls.manifest = json.loads(read(converted / "handover_manifest.json"))

    def changed(self, pid, text):
        return replace(self.draft, paragraphs=tuple(replace(p, text=text) if p.paragraph_id == pid else p
                                                    for p in self.draft.paragraphs))

    def test_full_document_roundtrip(self):
        self.assertEqual(render(self.draft, self.manifest), read(ROOT / "inputs/source/draft_v0.md"))
        self.assertEqual({p.section for p in self.draft.paragraphs},
                         {"abstract", "introduction", "related_work", "methodology", "experiments", "conclusion"})
        self.assertEqual(len(self.draft.paragraphs), 39)

    def test_all_claims_are_mapped_to_present_paragraphs(self):
        mapped = {c for p in self.draft.paragraphs for c in p.claim_ids}
        self.assertEqual(mapped, {c.claim_id for c in self.package.claims})
        self.assertEqual(len(mapped), 49)

    def test_source_claims_have_evidence_and_original_citations(self):
        source_claims = {c.claim_id: c for c in self.package.claims if c.kind == "source"}
        evidence = {e.evidence_id: e for e in self.package.evidence}
        from src.writing.contracts import CITATION
        for p in self.draft.paragraphs:
            required = {evidence[e].source_id for cid in p.claim_ids if cid in source_claims
                        for e in source_claims[cid].evidence_ids}
            self.assertLessEqual(required, set(CITATION.findall(p.text)))

    def test_four_tables_and_all_headings_survive(self):
        tables = [b for b in self.manifest["blocks"] if b["kind"] == "table"]
        self.assertEqual(len(tables), 4)
        self.assertTrue(all(b["locked"] for b in tables))
        original = read(ROOT / "inputs/source/draft_v0.md")
        restored = render(self.draft, self.manifest)
        self.assertEqual([x for x in original.splitlines() if x.startswith("#")],
                         [x for x in restored.splitlines() if x.startswith("#")])
        for table in tables:
            self.assertIn(table["original_text"], restored)

    def test_identity_passes_fixed_content_checks_only(self):
        self.assertEqual(deterministic(self.package, self.draft, ()).status, "PASS")
        self.assertEqual(deterministic(self.package, self.draft, (self.draft,)).status, "PASS")

    def test_changed_planned_item_count_is_rejected(self):
        p = next(p for p in self.draft.paragraphs if "planned pilot contains 20" in p.text)
        candidate = self.changed(p.paragraph_id, p.text.replace("contains 20", "contains 21", 1))
        result = deterministic(self.package, candidate, (self.draft,))
        self.assertEqual(result.status, "MAJOR_DRIFT")
        self.assertIn("numbers changed", result.reasons[0])

    def test_changed_page_specific_citation_is_rejected(self):
        p = next(p for p in self.draft.paragraphs if "[[S01]]" in p.text)
        candidate = self.changed(p.paragraph_id, p.text.replace("[[S01]]", "[[S02]]", 1))
        self.assertEqual(deterministic(self.package, candidate, (self.draft,)).status, "CITATION_MISMATCH")
        with self.assertRaises(ValueError):
            render(candidate, self.manifest)

    def test_table_word_change_is_rejected_before_model_call(self):
        block = next(b for b in self.manifest["blocks"] if b["kind"] == "table")
        candidate = self.changed(block["paragraph_id"], block["converted_text"].replace("Study", "Paper", 1))
        gate = LockedTablesGate(SemanticGate(NoModel()), self.manifest)
        result = gate.check(self.package, candidate, (self.draft,))
        self.assertEqual(result.status, "MAJOR_DRIFT")
        self.assertIn("locked table changed", result.reasons[0])

    def test_uncertainty_is_not_marked_as_approved(self):
        self.assertEqual(self.manifest["status"], "PROVISIONAL_NOT_TEAM_A_APPROVED")
        self.assertEqual(len(self.manifest["source_support_warnings"]), 4)
        self.assertEqual(self.package.study_status, "proposed")
        self.assertEqual(self.summary["semantic_grounding"], "NOT_CHECKED")

    def test_missing_model_check_fails_closed(self):
        gate = LockedTablesGate(SemanticGate(NoModel()), self.manifest)
        self.assertEqual(gate.check(self.package, self.draft).status, "CHECK_ERROR")


def verify():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HandoverTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    package = ResearchPackage.from_dict(json.loads(read(ROOT / "inputs/converted/research_package.json")))
    draft = Draft.from_dict(json.loads(read(ROOT / "inputs/converted/v0.json")), package)
    diagnostics = diagnose(draft)
    output = {"tests_run": result.testsRun, "passed": result.wasSuccessful(),
              "model_calls": 0, "semantic_grounding": "NOT_CHECKED", "team_a_approval": "PENDING",
              "rule_review_count": diagnostics["score"],
              "interpretation": "Format, roundtrip and fixed-content control tests; no live-model quality or grounding result."}
    write_json(ROOT / "verification/offline_summary.json", output)
    write_json(ROOT / "verification/v0_rule_diagnostics.json", diagnostics)
    print(json.dumps(output, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(verify())
