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
# A real rewrite of P002 from the first live run (scores 75 -> 35), with its citation tokens.
P002_REWRITE = ("When a language model is used to evaluate answers, the evaluator itself becomes an object of "
                "assessment. Multilingual studies already examine this problem. Fu and Liu evaluate judgments on "
                "parallel language versions, and Chung and Freienthal investigate cross-language stability in "
                "controlled customer-support dialogues. Their work gives direct precedents for studying "
                "language-dependent evaluation, not evidence that multilingual judging has been overlooked. "
                "[[S01]]; [[S02]].")


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

    def test_safe_rewrite_is_kept_and_reported(self):
        report, final, writer = self.run_pipeline([self.text.replace(BEFORE, GOOD)])
        record = report["paragraphs"][0]
        self.assertEqual(record["outcome"], "revised")
        self.assertLess(record["score_after"], record["score_before"] - pipeline.MIN_GAIN)
        self.assertIn(GOOD, checks.paragraph(final, TARGET).text)
        # Still above the target, so the writer was asked to improve the safe version further.
        self.assertGreater(record["score_after"], pipeline.THRESHOLD)
        self.assertEqual(len(writer.calls), pipeline.MAX_ATTEMPTS)
        self.assertIn("still scores", writer.calls[1][1])
        self.assertEqual(writer.calls[1][2]["paragraph"], self.text.replace(BEFORE, GOOD))
        self.assertTrue((self.output / "change_report.md").exists())
        self.assertTrue((self.output / "final_paper.md").exists())

    def test_rewrite_that_does_not_lower_the_score_is_not_kept(self):
        same_score = self.text.replace("whole underlying items", "the whole underlying items")
        report, final, _ = self.run_pipeline([same_score])
        record = report["paragraphs"][0]
        self.assertEqual(record["outcome"], "kept original")
        self.assertIn("not at least", record["attempts"][0]["verdict"])
        self.assertEqual(final, self.v0)

    def test_rejected_attempt_is_explained_to_the_writer_then_fixed(self):
        good = self.text.replace(BEFORE, GOOD)
        bad = good.replace("95%", "90%")
        report, _, writer = self.run_pipeline([bad, good])
        attempts = report["paragraphs"][0]["attempts"]
        self.assertEqual([a["accepted"] for a in attempts[:2]], [False, True])
        self.assertIn("numbers changed", attempts[0]["verdict"])
        self.assertIn("numbers changed", writer.calls[1][1])  # the reason is fed back into the next prompt
        self.assertEqual(report["paragraphs"][0]["outcome"], "revised")

    def test_three_failures_keep_the_original(self):
        bad = self.text.replace(BEFORE, GOOD) + " Pilot results show a clear language gap."
        report, final, writer = self.run_pipeline([bad])
        self.assertEqual(report["paragraphs"][0]["outcome"], "kept original")
        self.assertEqual(len(writer.calls), pipeline.MAX_ATTEMPTS)
        self.assertEqual(final, self.v0)

    def test_rewrite_reaching_the_target_stops_early(self):
        text = checks.paragraph(self.v0, "P002").text
        report, _, writer = self.run_pipeline([P002_REWRITE], only=("P002",))
        record = report["paragraphs"][0]
        self.assertEqual(record["outcome"], "revised")
        self.assertLessEqual(record["score_after"], pipeline.THRESHOLD)
        self.assertEqual(len(writer.calls), 1)
        self.assertNotEqual(text, P002_REWRITE)

    def test_evidence_failure_blocks_a_cited_paragraph(self):
        report, final, _ = self.run_pipeline([P002_REWRITE], evidence_status="UNSUPPORTED_ADDITION", only=("P002",))
        self.assertEqual(report["paragraphs"][0]["outcome"], "kept original")
        self.assertIn("evidence check", report["paragraphs"][0]["attempts"][0]["verdict"])
        self.assertEqual(final, self.v0)

    def test_malformed_checker_answer_is_asked_again_once(self):
        answers = []

        def flaky(payload, n):
            answers.append(n)
            if n == 1:  # first answer lists a claim twice, as seen in a live run
                good = meaning_pass(payload, n)
                good["paragraphs"][0]["checked_claim_ids"] *= 2
                return good
            return meaning_pass(payload, n)

        writer = Provider("writer", lambda payload, n: {"paragraph": P002_REWRITE})
        gate = checks.EvidenceGate(Provider("evidence", evidence("PASS")), checks.EvidenceIndex(self.package))
        report, _ = pipeline.run(self.package, self.v0, self.manifest, self.model, writer, RunStore(self.output),
                                 evidence_gate=gate, semantic_gate=SemanticGate(Provider("checker", flaky)),
                                 only={"P002"})
        self.assertEqual(report["paragraphs"][0]["outcome"], "revised")
        self.assertEqual(len(answers), 2)
        self.assertEqual(len(writer.calls), 1)  # no writer attempt was wasted

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
