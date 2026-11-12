"""Offline checks for the Half 2 pipeline and its checks (scripted models, no API calls)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

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
    """A well-formed evidence reply: audits the rewrite's first sentence."""
    def reply(payload, _):
        first = checks.plain(payload["rewrite"]).split(". ")[0]
        label = "SUPPORTED" if status == "PASS" else "UNSUPPORTED"
        return {"status": status, "sentences": [{"sentence": first, "label": label, "evidence": "quote"}],
                "reasons": [] if status == "PASS" else ["Scripted."], "pre_existing": []}
    return reply


class Critic:
    """Stands in for Guan Hong's QualitativeCritic: returns fixed findings or fails."""
    model = "critic"

    def __init__(self, paragraphs, fail=False):
        self.paragraphs, self.fail, self.labels = paragraphs, fail, []

    def assess(self, package, draft, label, store):
        self.labels.append(label)
        if self.fail:
            raise ValueError("duplicate finding")
        return {"paragraphs": self.paragraphs}


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

    def run_pipeline(self, rewrites, evidence_status="PASS", only=(TARGET,), critic=None, evidence_provider=None,
                     require_critic=False):
        writer = Provider("writer", lambda payload, n: {"paragraph": rewrites[min(n, len(rewrites)) - 1]})
        checker = Provider("checker", meaning_pass)
        self.evidence_provider = evidence_provider or Provider("evidence", evidence(evidence_status))
        gate = checks.EvidenceGate(self.evidence_provider, checks.EvidenceIndex(self.package).learn_authors(self.v0))
        report, final = pipeline.run(self.package, self.v0, self.manifest, self.model, writer, RunStore(self.output),
                                     evidence_gate=gate, semantic_gate=SemanticGate(checker), critic=critic,
                                     only=set(only), require_critic=require_critic)
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

    def test_critic_notes_reach_the_writer_and_the_report(self):
        critic = Critic([{"paragraph_id": TARGET, "findings": [
            {"criterion": "formulaic_language", "status": "ACTIONABLE", "quote": BEFORE,
             "explanation": "Stock contrast.", "safe_action": "State it directly."},
            {"criterion": "argument_strength", "status": "ACTIONABLE", "quote": "",
             "explanation": "Clause order.", "safe_action": "Lead with the finding."}]},
            {"paragraph_id": "P002", "findings": [
            {"criterion": "argument_strength", "status": "NEEDS_RESEARCH", "quote": "",
             "explanation": "Interval method needs a citation.", "safe_action": ""}]}])
        report, _, writer = self.run_pipeline([self.text.replace(BEFORE, GOOD)], critic=critic)
        self.assertIn("Stock contrast.", writer.calls[0][1])
        c = report["critic"]
        self.assertEqual((c["review_of_v0"], c["actionable_before"]), ("ok", 2))
        self.assertEqual(c["needs_research"][0]["paragraph_id"], "P002")
        self.assertEqual(critic.labels, ["v0_review", "final_review"])

    def test_failed_critic_review_does_not_stop_the_run(self):
        critic = Critic(None, fail=True)
        report, final, _ = self.run_pipeline([self.text.replace(BEFORE, GOOD)], critic=critic)
        self.assertEqual(report["paragraphs"][0]["outcome"], "revised")
        self.assertTrue(report["critic"]["review_of_v0"].startswith("unavailable"))
        # asked again under a new name each time: the run store refuses to overwrite a file
        self.assertEqual(critic.labels[:3], ["v0_review", "v0_review_retry1", "v0_review_retry2"])
        self.assertIn("try 3", report["critic"]["review_of_v0"])

    def test_live_runs_stop_before_rewriting_if_the_critic_cannot_review_v0(self):
        with self.assertRaises(pipeline.CriticUnavailable):
            self.run_pipeline([self.text.replace(BEFORE, GOOD)], critic=Critic(None, fail=True), require_critic=True)

    def test_the_critic_cannot_be_switched_off_from_the_command_line(self):
        with self.assertRaises(SystemExit):
            pipeline.main(["--output", "x", "--writer-model", "a", "--checker-model", "b", "--no-critic"])

    def test_paragraphs_needing_research_are_not_rewritten(self):
        critic = Critic([{"paragraph_id": TARGET, "findings": [
            {"criterion": "argument_strength", "status": "NEEDS_RESEARCH", "quote": "",
             "explanation": "Needs a source.", "safe_action": ""}]}])
        report, final, writer = self.run_pipeline([self.text.replace(BEFORE, GOOD)], critic=critic)
        record = report["paragraphs"][0]
        self.assertEqual(record["outcome"], "held for research")
        self.assertEqual((record["attempts"], writer.calls), ([], []))
        self.assertEqual(report["totals"]["held_for_research"], 1)
        self.assertEqual(final, self.v0)

    def test_evidence_reply_is_validated_in_full(self):
        rewrite = "Smith et al. reported a gain. We then test it. [[S01]]"
        original = "Smith et al. reported a small gain. We then test it. [[S01]]"
        ok = lambda **kw: {"status": "PASS", "reasons": [], "pre_existing": [],
                           "sentences": [{"sentence": "Smith et al. reported a gain.", "label": "SUPPORTED", "evidence": "q"}], **kw}
        self.assertEqual(checks.validate_evidence_reply(ok(), original, rewrite).status, "PASS")
        bad_replies = [
            {"status": "PASS", "reasons": [], "pre_existing": []},                     # missing field
            ok(sentences=[]),                                                         # empty audit
            ok(sentences=[{"sentence": "Jones found nothing.", "label": "SUPPORTED", "evidence": "q"}]),  # not in rewrite
            ok(sentences=[{"sentence": "Smith et al. reported a gain.", "label": "CONTRADICTED", "evidence": "q"}]),  # PASS + new problem
        ]
        for reply in bad_replies:
            with self.assertRaises(ValueError):
                checks.validate_evidence_reply(reply, original, rewrite)
        # a problem already in the original may pass (it is not the rewrite's fault)
        same = ok(sentences=[{"sentence": "We then test it.", "label": "UNSUPPORTED", "evidence": ""}])
        self.assertEqual(checks.validate_evidence_reply(same, original, rewrite).status, "PASS")

    def test_malformed_evidence_reply_is_retried_then_fails_closed(self):
        broken = Provider("evidence", lambda payload, _: {"status": "PASS"})       # no sentences: used to crash
        text = checks.paragraph(self.v0, TARGET).text.replace(BEFORE, GOOD)
        rewrite = text.replace("A non-significant contrast", "As Yu et al. show, a non-significant contrast")
        report, final, _ = self.run_pipeline([rewrite], evidence_provider=broken)
        record = report["paragraphs"][0]
        self.assertEqual(record["outcome"], "kept original")
        self.assertEqual(record["attempts"][0]["checks"][-1]["status"], "CHECK_ERROR")
        self.assertEqual(final, self.v0)
        self.assertEqual(len(broken.calls), 2 * 3)  # asked twice per attempt, three attempts, never crashed

    def test_too_small_a_change_pushes_the_writer_harder(self):
        report, _, writer = self.run_pipeline([self.text, self.text.replace(BEFORE, GOOD)])
        self.assertEqual(report["paragraphs"][0]["attempts"][0]["checks"][0]["status"], "NO_CHANGE")
        self.assertIn("changed too little", writer.calls[1][1])
        self.assertEqual(report["paragraphs"][0]["outcome"], "revised")

    def test_named_author_without_citation_triggers_the_evidence_check(self):
        provider = Provider("evidence", evidence("UNSUPPORTED_ADDITION"))
        text = checks.paragraph(self.v0, TARGET).text.replace(BEFORE, GOOD)
        rewrite = text.replace("A non-significant contrast", "As Yu et al. show, a non-significant contrast")
        report, final, _ = self.run_pipeline([rewrite], evidence_provider=provider)
        self.assertEqual(report["paragraphs"][0]["outcome"], "kept original")
        self.assertIn("evidence check", report["paragraphs"][0]["attempts"][0]["verdict"])
        sent = provider.calls[0][2]["evidence"]
        self.assertEqual([(e["paper_id"], e["named_as"]) for e in sent], [("2025.emnlp-main.712", ["Yu et al."])])

    def test_authors_are_learned_from_v0(self):
        index = checks.EvidenceIndex(self.package).learn_authors(self.v0)
        self.assertEqual(sorted(index.papers_of_author["Wang et al."]), ["2025.emnlp-main.103"])
        self.assertEqual(sorted(index.papers_of_author["Chung and Freienthal"]), ["2026.mme-main.8"])
        self.assertNotIn("Datta and Baitalik", index.papers_of_author)  # table row: ambiguous, not guessed

    def test_default_topic_is_the_reviewed_example(self):
        package, v0, manifest, facts, label = pipeline.load_topic()
        self.assertEqual((label, v0), ("cluster7", self.v0))
        self.assertEqual(facts, checks.FACTS_FILE)

    def test_any_topic_folder_loads_like_an_upload_and_uses_its_own_facts(self):
        folder = self.output.parent / "topic_x" / "handover"
        folder.mkdir(parents=True)
        for name in ("research_package.json", "v0.json"):
            (folder / name).write_bytes((ROOT / "inputs/converted" / name).read_bytes())
        package, v0, manifest, facts, label = pipeline.load_topic(str(folder))
        self.assertEqual(label, "topic_x")
        self.assertEqual(facts, checks.FACTS_FILE)  # no topic table -> shared table
        self.assertTrue(pipeline.select(v0, manifest, self.model))
        (folder / "master_facts.xlsx").write_bytes(checks.FACTS_FILE.read_bytes())
        self.assertEqual(pipeline.load_topic(str(folder))[3], folder / "master_facts.xlsx")

    def test_topic_ids_come_from_the_half1_topic_list(self):
        folder = self.output.parent / "cluster99" / "handover"
        folder.mkdir(parents=True)
        for name in ("research_package.json", "v0.json"):
            (folder / name).write_bytes((ROOT / "inputs/converted" / name).read_bytes())
        index = self.output.parent / "index.json"
        index.write_text(json.dumps({"topics": [
            {"id": "cluster99", "package": str((folder / "research_package.json").relative_to(ROOT.parent))}]}))
        with patch.object(pipeline, "TOPIC_INDEX", index):
            self.assertEqual(pipeline.load_topic("cluster99")[4], "cluster99")
            with self.assertRaisesRegex(ValueError, "choose from cluster99"):
                pipeline.load_topic("cluster42")

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
