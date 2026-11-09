"""Offline checks for the Half 2 pipeline and its checks (scripted models, no API calls)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from project_io import read_input
from src.writing.preservation import SemanticGate
from src.writing.storage import RunStore

import half2_checks as checks
import half2_pipeline as pipeline

ROOT = Path(__file__).resolve().parent
TARGET = "P035"
BEFORE = "reported rather than replaced by favorable summaries"
GOOD = "reported as they are, not replaced by favorable summaries"


class Provider:
    test_only = True

    def __init__(self, model, respond):
        self.model, self.respond, self.calls = model, respond, []

    def generate(self, task, instructions, payload, schema, max_output_tokens):
        self.calls.append((task, instructions, payload))
        return self.respond(payload, len(self.calls))


def meaning_pass(payload, _):
    return {"global_status": "PASS", "global_reasons": [],
            "paragraphs": [{"paragraph_id": p["paragraph_id"], "checked_claim_ids": p["claim_ids"],
                            "status": "PASS", "reasons": []} for p in payload["candidate"]["paragraphs"]]}


def evidence(status):
    return lambda payload, _: {"status": status, "sentences": [], "reasons": [] if status == "PASS" else ["Scripted."],
                               "pre_existing": []}


class Half2Tests(unittest.TestCase):
    def setUp(self):
        self.package, self.v0, self.manifest = read_input(ROOT / "inputs/converted")
        self.model = json.loads(pipeline.MODEL_FILE.read_text(encoding="utf-8"))
        temp_root = ROOT / ".test-work"
        temp_root.mkdir(exist_ok=True)
        directory = TemporaryDirectory(dir=temp_root)
        self.addCleanup(directory.cleanup)
        self.output = Path(directory.name) / "run"
        self.text = checks.paragraph(self.v0, TARGET).text

    def run_pipeline(self, rewrites, evidence_status="PASS", only=(TARGET,)):
        writer = Provider("writer", lambda payload, n: {"paragraph": rewrites[min(n, len(rewrites)) - 1]})
        checker = Provider("checker", meaning_pass)
        gate = checks.EvidenceGate(Provider("evidence", evidence(evidence_status)), checks.EvidenceIndex(self.package))
        report, final = pipeline.run(self.package, self.v0, self.manifest, self.model, writer, RunStore(self.output),
                                     evidence_gate=gate, semantic_gate=SemanticGate(checker), only=set(only))
        return report, final, writer

    def test_safe_rewrite_is_accepted_and_reported(self):
        report, final, writer = self.run_pipeline([self.text.replace(BEFORE, GOOD)])
        record = report["paragraphs"][0]
        self.assertEqual(record["outcome"], "revised")
        self.assertLess(record["score_after"], record["score_before"])
        self.assertEqual(len(writer.calls), 1)
        self.assertIn(GOOD, checks.paragraph(final, TARGET).text)
        self.assertTrue((self.output / "change_report.md").exists())
        self.assertTrue((self.output / "final_paper.md").exists())

    def test_rejected_attempt_is_explained_to_the_writer_then_fixed(self):
        bad = self.text.replace("95%", "90%")
        report, _, writer = self.run_pipeline([bad, self.text.replace(BEFORE, GOOD)])
        attempts = report["paragraphs"][0]["attempts"]
        self.assertEqual([a["accepted"] for a in attempts], [False, True])
        self.assertIn("numbers changed", attempts[0]["verdict"])
        self.assertIn("numbers changed", writer.calls[1][1])  # the reason is fed back into the next prompt

    def test_three_failures_keep_the_original(self):
        bad = self.text + " Pilot results show a clear language gap."
        report, final, writer = self.run_pipeline([bad])
        self.assertEqual(report["paragraphs"][0]["outcome"], "kept original")
        self.assertEqual(len(writer.calls), pipeline.MAX_ATTEMPTS)
        self.assertEqual(final, self.v0)

    def test_evidence_failure_blocks_a_cited_paragraph(self):
        text = checks.paragraph(self.v0, "P002").text
        rewrite = text.replace("becomes an object of assessment", "has to be assessed")
        report, final, _ = self.run_pipeline([rewrite], evidence_status="UNSUPPORTED_ADDITION", only=("P002",))
        self.assertEqual(report["paragraphs"][0]["outcome"], "kept original")
        self.assertIn("evidence check", report["paragraphs"][0]["attempts"][0]["verdict"])
        self.assertEqual(final, self.v0)

    def test_evidence_index_maps_citations_to_the_evidence_table(self):
        found = checks.EvidenceIndex(self.package).for_text(checks.paragraph(self.v0, "P008").text)
        self.assertEqual([f["paper_id"] for f in found], ["2025.emnlp-main.712", "2026.mme-main.8"])
        self.assertTrue(all(f["evidence_table"] for f in found))

    def test_negated_certainty_is_not_a_stronger_claim(self):
        text = checks.paragraph(self.v0, "P037").text
        self.assertTrue(checks.no_new_facts_check(self.package, self.v0, "P037", text).passed)
        stronger = text.replace("It cannot establish broad", "It clearly shows broad")
        self.assertFalse(checks.no_new_facts_check(self.package, self.v0, "P037", stronger).passed)


if __name__ == "__main__":
    unittest.main()
