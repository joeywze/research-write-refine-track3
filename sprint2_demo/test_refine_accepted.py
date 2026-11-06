"""Regression checks for the optional revision of the accepted Sprint 2 draft."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from refine_accepted import MODEL_FILE, accepted_inputs, refine_accepted
from src.writing.critic import validate_critique
from src.writing.evaluation import read_json
from src.writing.prompts import CRITERIA
from src.writing.storage import RunStore


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs/live-20261026T000828046240Z"
TARGET = "P002"
BEFORE = "Multilingual studies already examine"
AFTER = "Multilingual studies examine"


def review_response(draft, actionable=False):
    related = next(p for p in draft["paragraphs"] if p["section"] == "conclusion")
    rows = []
    for paragraph in draft["paragraphs"]:
        findings = []
        for criterion in CRITERIA:
            flag = actionable and paragraph["paragraph_id"] == TARGET and criterion == "specificity"
            quote = BEFORE if BEFORE in paragraph["text"] else AFTER
            findings.append({"criterion": criterion, "status": "ACTIONABLE" if flag else "NO_ISSUE",
                             "quote": quote if flag else "", "explanation": "Scripted review.",
                             "safe_action": "Tighten the opening." if flag else "",
                             "related_paragraph_id": related["paragraph_id"] if flag else "",
                             "related_quote": related["text"][:30] if flag else ""})
        rows.append({"paragraph_id": paragraph["paragraph_id"], "findings": findings})
    return {"paragraphs": rows}


class Provider:
    test_only = True

    def __init__(self, model, respond):
        self.model = model
        self.respond = respond
        self.calls = []

    def generate(self, task, instructions, payload, schema, max_output_tokens):
        self.calls.append(payload)
        return self.respond(payload, len(self.calls))


class AcceptedDraftTests(unittest.TestCase):
    def setUp(self):
        self.inputs = accepted_inputs(RUN, ROOT / "inputs/converted")
        self.model = read_json(MODEL_FILE)
        temp_root = ROOT / ".test-work"
        temp_root.mkdir(exist_ok=True)
        directory = TemporaryDirectory(dir=temp_root)
        self.addCleanup(directory.cleanup)
        self.output = Path(directory.name) / "refinement"

    def run_pass(self, verdict, actionable=True, resolves=True):
        def rewrite(payload, _):
            paragraph = next(p for p in payload["draft"]["paragraphs"] if p["paragraph_id"] == TARGET)
            self.assertIn("language-dependent evaluation", paragraph["text"])
            self.assertEqual(payload["allowed_paragraph_ids"], [TARGET])
            return {"edits": [{"paragraph_id": TARGET, "text": paragraph["text"].replace(BEFORE, AFTER)}],
                    "review_responses": [{"finding_id": "L:P002:specificity", "decision": "EDITED",
                                          "explanation": "Removed a redundant adverb.",
                                          "before_quote": BEFORE, "after_quote": AFTER}]}

        def check(payload, _):
            original, accepted = payload["references"]
            original_text = next(p["text"] for p in original["paragraphs"] if p["paragraph_id"] == TARGET)
            accepted_text = next(p["text"] for p in accepted["paragraphs"] if p["paragraph_id"] == TARGET)
            self.assertIn("this problem", original_text)
            self.assertIn("language-dependent evaluation", accepted_text)
            return {"global_status": verdict, "global_reasons": [] if verdict == "PASS" else ["Scripted drift."],
                    "paragraphs": [{"paragraph_id": p["paragraph_id"], "checked_claim_ids": p["claim_ids"],
                                    "status": "PASS", "reasons": []} for p in payload["candidate"]["paragraphs"]]}

        writer = Provider("writer", rewrite)
        checker = Provider("checker", check)
        def critique(payload, call_number):
            return review_response(payload["draft"], actionable and (call_number == 1 or not resolves))

        reviewer = Provider("reviewer", critique)
        result = refine_accepted(self.inputs, self.model, writer, checker, reviewer,
                                 RunStore(self.output), writer_cap=16000, review_cap=32000)
        return result, writer, checker, reviewer

    def test_accepted_v2_is_preserved_as_parent_and_context_is_reassessed(self):
        result, writer, checker, reviewer = self.run_pass("PASS")
        self.assertTrue(result["accepted_edit"])
        self.assertEqual(result["guided_attempts_including_this_pass"], 2)
        self.assertEqual(len(checker.calls), 1)
        self.assertEqual(len(reviewer.calls), 2)
        self.assertEqual(reviewer.calls[0]["paragraph_ids_to_assess"], reviewer.calls[1]["paragraph_ids_to_assess"])
        initial = read_json(self.output / "accepted_v2.json")
        final = read_json(self.output / "guided_final.json")
        self.assertEqual([a["paragraph_id"] for a, b in zip(initial["paragraphs"], final["paragraphs"]) if a != b],
                         [TARGET])
        self.assertTrue((self.output / "guided_final_with_layout.md").exists())

    def test_failed_meaning_check_keeps_v2(self):
        result, _, checker, reviewer = self.run_pass("MAJOR_DRIFT")
        self.assertFalse(result["accepted_edit"])
        self.assertEqual(result["stop_reason"], "PRESERVATION_FAILED")
        self.assertEqual((len(checker.calls), len(reviewer.calls)), (1, 1))
        self.assertEqual(read_json(self.output / "guided_final.json"), read_json(self.output / "accepted_v2.json"))

    def test_edit_without_resolving_a_review_point_keeps_v2(self):
        result, _, _, reviewer = self.run_pass("PASS", resolves=False)
        self.assertFalse(result["accepted_edit"])
        self.assertEqual(result["stop_reason"], "INSUFFICIENT_IMPROVEMENT")
        self.assertEqual(len(reviewer.calls), 2)

    def test_detector_hints_without_actionable_review_do_not_trigger_rewrite(self):
        result, writer, checker, reviewer = self.run_pass("PASS", actionable=False)
        self.assertEqual(result["stop_reason"], "NO_ACTIONABLE_DIAGNOSTICS")
        self.assertTrue(reviewer.calls[0]["detector_hints"])
        self.assertFalse(writer.calls or checker.calls)
        self.assertEqual(result["guided_attempts_including_this_pass"], 1)

    def test_invalid_cross_section_quote_is_rejected(self):
        _, _, v2, _, editable, _ = self.inputs
        raw = review_response(read_json(RUN / "guided_final.json"), actionable=True)
        target = next(p for p in raw["paragraphs"] if p["paragraph_id"] == TARGET)
        target["findings"][0]["related_quote"] = "A quote absent from the related paragraph."
        with self.assertRaisesRegex(ValueError, "Cross-section quote"):
            validate_critique(raw, v2, editable_ids=editable)

    def test_used_up_attempt_budget_blocks_the_optional_pass(self):
        provider = Provider("never called", lambda *_: self.fail("Model called"))
        with self.assertRaisesRegex(ValueError, "all three"):
            refine_accepted((*self.inputs[:-1], 3), self.model, provider, provider, provider,
                            RunStore(self.output), writer_cap=16000, review_cap=32000)
