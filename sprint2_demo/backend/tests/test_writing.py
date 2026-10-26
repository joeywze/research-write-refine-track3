from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from src.writing.contracts import Draft, ResearchPackage, digest
from src.writing.demo import FixtureProvider, fixture_inputs, remove_transitions, run_demo
from src.writing.diagnostics import diagnose
from src.writing.evaluation import export_human, held_out_audit, read_json
from src.writing.pipeline import RunConfig, run_study
from src.writing.preservation import SemanticGate, deterministic
from src.writing.providers import BudgetExceeded, OpenAIJSON, TokenBudget
from src.writing.revision import apply_edits
from src.writing.storage import RunStore


def local_temp():
    project = Path(__file__).resolve().parents[1]
    parent = (project / ".test-work").resolve()
    if not parent.is_relative_to(project):
        raise ValueError("Test temporary directory escaped the project")
    parent.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=parent)


class Scripted:
    test_only = True

    def __init__(self, responses, model="fixture-writer"):
        self.responses = list(responses)
        self.calls = []
        self.model = model

    def generate(self, task, instructions, payload, schema, max_output_tokens):
        self.calls.append((task, payload))
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class WritingTests(unittest.TestCase):
    def setUp(self):
        self.package, self.v0, self.approved = fixture_inputs()
        self.temp = local_temp()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def candidate(self, old, new, pid="p_abstract"):
        p = next(p for p in self.v0.paragraphs if p.paragraph_id == pid)
        return apply_edits(self.v0, {"edits": [{"paragraph_id": pid, "text": p.text.replace(old, new)}]}, (pid,))

    def gate(self):
        return SemanticGate(FixtureProvider("fixture-auditor", self.approved))

    def study(self, guided, generic=None, gate=None, name="run"):
        baseline = FixtureProvider("fixture-writer")
        return run_study(self.package, self.v0, baseline, self.gate(),
                         {"generic": (generic or FixtureProvider("fixture-writer"), self.gate()),
                          "guided": (guided, gate or self.gate())},
                         RunStore(self.root / name))

    def test_contract_rejects_results_in_proposal(self):
        raw = asdict(self.package)
        raw["claims"][0]["kind"] = "result"
        with self.assertRaises(ValueError):
            ResearchPackage.from_dict(raw)

    def test_contract_unknown_evidence_and_schema(self):
        for key, value in (("schema_version", "99"), ("unexpected", True)):
            raw = asdict(self.package)
            raw[key] = value
            with self.assertRaises(ValueError):
                ResearchPackage.from_dict(raw)
        raw = json.loads(json.dumps(asdict(self.package)))
        raw["claims"][0]["evidence_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            ResearchPackage.from_dict(raw)

    def test_all_sections_and_claims_required(self):
        raw = json.loads(json.dumps(asdict(self.v0)))
        raw["paragraphs"].pop()
        with self.assertRaises(ValueError):
            Draft.from_dict(raw, self.package)

    def test_claim_citation_required_locally(self):
        raw = json.loads(json.dumps(asdict(self.v0)))
        raw["paragraphs"][0]["text"] = raw["paragraphs"][0]["text"].replace("[[Sdemo]]", "")
        with self.assertRaises(ValueError):
            Draft.from_dict(raw, self.package)

    def test_no_side_effects_from_import(self):
        # Pure package imports do not require an SDK, credentials, datasets or network.
        import src.writing.__main__
        self.assertTrue(callable(src.writing.__main__.main))

    def test_demo_transition_removal_keeps_capitals_and_acronyms(self):
        self.assertEqual(remove_transitions("Moreover, this is a plan. Furthermore, RAG is relevant."),
                         "This is a plan. RAG is relevant.")

    def test_short_and_punctuation_are_not_applicable(self):
        tiny = replace(self.v0, paragraphs=tuple(replace(p, text="...") for p in self.v0.paragraphs))
        self.assertIsNone(diagnose(tiny)["score"])
        self.assertFalse(diagnose(tiny)["applicable"])

    def test_targeted_edits_preserve_other_paragraphs(self):
        c = self.candidate("Moreover, ", "")
        self.assertEqual(c.paragraphs[1:], self.v0.paragraphs[1:])
        with self.assertRaises(ValueError):
            apply_edits(self.v0, {"edits": [{"paragraph_id": "p_conclusion", "text": "Changed."}]}, ("p_abstract",))

    def test_duplicate_and_split_edits_rejected(self):
        for edits in ([{"paragraph_id": "p_abstract", "text": "A."}] * 2,
                      [{"paragraph_id": "p_abstract", "text": "A.\n\nB."}],
                      [{"paragraph_id": "p_abstract", "text": "A.\r\n  \r\nB."}]):
            with self.assertRaises(ValueError):
                apply_edits(self.v0, {"edits": edits}, ("p_abstract",))

    def test_numbers_citations_and_terms_protected(self):
        for before, after, status in (("20", "21", "MAJOR_DRIFT"),
                                       ("[[Sdemo]]", "[[Sdemo]][[Sdemo]]", "CITATION_MISMATCH"),
                                       ("time-ordered validation", "random splitting", "MAJOR_DRIFT")):
            report = deterministic(self.package, self.candidate(before, after), (self.v0,))
            self.assertEqual(report.status, status)

    def test_dropped_and_unknown_citations_are_labelled(self):
        for changed in ("", "[[Unknown]]"):
            self.assertEqual(deterministic(self.package, self.candidate("[[Sdemo]]", changed),
                                           (self.v0,)).status, "CITATION_MISMATCH")

    def test_equations_protected(self):
        base = replace(self.v0, paragraphs=(replace(self.v0.paragraphs[0], text=self.v0.paragraphs[0].text + " $x+y$"),
                                           *self.v0.paragraphs[1:]))
        changed = replace(base, paragraphs=(replace(base.paragraphs[0], text=base.paragraphs[0].text.replace("x+y", "x-y")),
                                              *base.paragraphs[1:]))
        self.assertEqual(deterministic(self.package, changed, (base,)).status, "MAJOR_DRIFT")

    def test_v0_unknown_number_rejected(self):
        self.assertEqual(deterministic(self.package, self.candidate("20", "999"), ()).status, "UNSUPPORTED_ADDITION")

    def test_semantic_uncertainty_drift_rejected(self):
        # Same numbers/citations, but proposal status has been removed: deterministic checks alone pass.
        c = self.candidate("this synthetic proposal compares", "this completed study validates")
        self.assertEqual(deterministic(self.package, c, (self.v0,)).status, "PASS")
        response = FixtureProvider("fixture-auditor", [digest(c)]).generate(
            "preservation", "", {"candidate_hash": digest(c), "candidate": asdict(c)}, {}, 1000)
        response["global_status"] = "MAJOR_DRIFT"
        response["global_reasons"] = ["Turns a proposal into a completed finding"]
        gate = SemanticGate(Scripted([response], "fixture-auditor"))
        self.assertEqual(gate.check(self.package, c, (self.v0,)).status, "MAJOR_DRIFT")

    def test_checker_error_and_incomplete_audit_fail_closed(self):
        for response in (RuntimeError("unavailable"), {"global_status": "PASS", "global_reasons": [], "paragraphs": []}):
            result = SemanticGate(Scripted([response], "fixture-auditor")).check(self.package, self.v0)
            self.assertEqual(result.status, "CHECK_ERROR")

    def test_checker_receives_both_references_but_no_diagnostics(self):
        c = self.candidate("Moreover, ", "")
        response = FixtureProvider("fixture-auditor", [digest(c)]).generate(
            "preservation", "", {"candidate_hash": digest(c), "candidate": asdict(c)}, {}, 1000)
        provider = Scripted([response], "fixture-auditor")
        self.assertEqual(SemanticGate(provider).check(self.package, c, (self.v0, self.v0)).status, "PASS")
        payload = provider.calls[0][1]
        self.assertEqual(len(payload["references"]), 2)
        self.assertNotIn("diagnostics", payload)
        self.assertNotIn("score", payload)

    def test_unknown_claim_audit_is_not_pass(self):
        response = FixtureProvider("fixture-auditor", self.approved).generate(
            "preservation", "", {"candidate_hash": digest(self.v0), "candidate": asdict(self.v0)}, {}, 1000)
        response["paragraphs"][0]["checked_claim_ids"] = []
        result = SemanticGate(Scripted([response], "fixture-auditor")).check(self.package, self.v0)
        self.assertEqual(result.status, "CHECK_ERROR")

    def test_rollback_retains_first_accepted_version(self):
        first = apply_edits(self.v0, {"edits": [{"paragraph_id": "p_abstract",
                                                "text": remove_transitions(self.v0.paragraphs[0].text)}]}, ("p_abstract",))
        responses = [{"edits": [{"paragraph_id": "p_abstract", "text": first.paragraphs[0].text}]},
                     {"edits": [{"paragraph_id": "p_related", "text": self.v0.paragraphs[2].text.replace("20", "21")}]}]
        result = self.study(Scripted(responses))
        self.assertEqual(result["results"]["guided"]["final_hash"], digest(first))
        self.assertEqual(len(result["results"]["guided"]["attempts"]), 2)

    def test_no_actionable_issues_makes_no_revision_calls(self):
        v0 = replace(self.v0, paragraphs=tuple(replace(p, text=remove_transitions(p.text)) for p in self.v0.paragraphs))
        writer = Scripted([])
        gate = SemanticGate(FixtureProvider("fixture-auditor", [digest(v0)]))
        result = run_study(self.package, v0, writer, gate,
                           {a: (writer, gate) for a in ("generic", "guided")}, RunStore(self.root / "quiet"))
        self.assertFalse(writer.calls)
        self.assertEqual(result["results"]["guided"]["stop_reason"], "NO_ACTIONABLE_DIAGNOSTICS")

    def test_grounding_gate_rejects_before_revision(self):
        writer = Scripted([])
        gate = SemanticGate(Scripted([RuntimeError("no audit")], "fixture-auditor"))
        store = RunStore(self.root / "bad_v0")
        with self.assertRaises(ValueError):
            run_study(self.package, self.v0, writer, gate,
                      {a: (writer, gate) for a in ("generic", "guided")}, store)
        self.assertFalse(writer.calls)
        self.assertFalse((store.directory / "v0_accepted.json").exists())

    def test_generated_v0_is_saved_and_gated_before_revision(self):
        writer = Scripted([asdict(self.v0)])
        result = run_study(self.package, None, writer, self.gate(),
                           {a: (FixtureProvider("fixture-writer"), self.gate()) for a in ("generic", "guided")},
                           RunStore(self.root / "generated"))
        self.assertEqual(writer.calls[0][0], "draft_v0")
        self.assertEqual(result["v0_hash"], digest(self.v0))
        self.assertTrue((self.root / "generated/v0_generation_response.json").exists())

    def test_malformed_generated_v0_retained_without_acceptance(self):
        with self.assertRaises(ValueError):
            run_study(self.package, None, Scripted([{"bad": "draft"}]), self.gate(),
                       {a: (FixtureProvider("fixture-writer"), self.gate()) for a in ("generic", "guided")},
                       RunStore(self.root / "malformed"))
        self.assertTrue((self.root / "malformed/v0_generation_response.json").exists())
        self.assertFalse((self.root / "malformed/v0_accepted.json").exists())

    def test_three_attempts_and_all_sections_saved(self):
        result = run_demo(self.root / "demo")
        summary = read_json(self.root / "demo/study_summary.json")
        attempts = summary["results"]["guided"]["attempts"]
        self.assertEqual(len(attempts), 3)
        self.assertTrue(all(a["accepted"] for a in attempts))
        self.assertEqual(result["stop_reason"], "MAX_ATTEMPTS")
        trace = (self.root / "demo/trajectory.csv").read_text()
        self.assertIn("candidate_score,accepted_score", trace)
        self.assertIn("guided,3,4,3,3", trace)
        self.assertIsNone(read_json(self.root / "demo/cost_summary.json")["stages"]["guided"]["charged_tokens"])
        self.assertTrue(all(x > y for x, y in zip([result["v0_score"], *result["guided_scores"]], result["guided_scores"])))
        with self.assertRaises(ValueError):
            RunConfig(max_attempts=4)

    def test_rejection_rolls_back_and_stops(self):
        bad = self.candidate("20", "21").paragraphs[0]
        result = self.study(Scripted([{"edits": [{"paragraph_id": bad.paragraph_id, "text": bad.text}]}]))
        guided = result["results"]["guided"]
        self.assertEqual(guided["final_hash"], digest(self.v0))
        self.assertEqual(len(guided["attempts"]), 1)
        self.assertEqual(guided["stop_reason"], "PRESERVATION_FAILED")
        self.assertTrue((self.root / "run/guided_1_candidate.json").exists())

    def test_repeated_and_invalid_response_stop(self):
        for i, raw in enumerate(({"edits": []}, {"not_edits": []})):
            result = self.study(Scripted([raw]), name=f"run{i}")
            self.assertEqual(len(result["results"]["guided"]["attempts"]), 1)
            self.assertEqual(result["results"]["guided"]["final_hash"], digest(self.v0))
            self.assertTrue((self.root / f"run{i}/guided_1_response.json").exists())

    def test_no_diagnostic_improvement_stops(self):
        c = self.candidate("The purpose is", "The aim is", "p_introduction")
        response = {"edits": [{"paragraph_id": "p_introduction", "text": c.paragraphs[1].text}]}
        gate = SemanticGate(FixtureProvider("fixture-auditor", [digest(c)]))
        result = self.study(Scripted([response]), gate=gate)
        guided = result["results"]["guided"]
        self.assertEqual(guided["stop_reason"], "INSUFFICIENT_IMPROVEMENT")
        self.assertEqual(guided["final_hash"], digest(self.v0))

    def test_budget_error_retains_v0(self):
        result = self.study(Scripted([BudgetExceeded("limit")]))
        self.assertEqual(result["results"]["guided"]["stop_reason"], "BUDGET_EXHAUSTED")
        self.assertEqual(result["results"]["guided"]["final_hash"], digest(self.v0))

    def test_same_model_checker_rejected(self):
        writer = FixtureProvider("same")
        gate = SemanticGate(FixtureProvider("same", self.approved))
        with self.assertRaises(ValueError):
            run_study(self.package, self.v0, writer, gate,
                      {a: (writer, gate) for a in ("generic", "guided")}, RunStore(self.root / "same"))

    def test_generic_gets_same_scope_without_diagnostics(self):
        raw = {"edits": []}
        generic, guided = Scripted([raw]), Scripted([raw])
        self.study(guided, generic)
        self.assertEqual(generic.calls[0][1]["allowed_paragraph_ids"], guided.calls[0][1]["allowed_paragraph_ids"])
        self.assertNotIn("diagnostics", generic.calls[0][1])
        self.assertIn("diagnostics", guided.calls[0][1])

    def test_human_export_blinds_and_deduplicates(self):
        run_demo(self.root / "demo")
        result = export_human([self.root / "demo"], self.root / "human")
        items = (self.root / "human/raters/writing_items.jsonl").read_text(encoding="utf-8")
        self.assertNotIn('"conditions"', items)
        self.assertNotIn('"score"', items)
        self.assertEqual(result["cases"], 1)
        keys = [json.loads(l) for l in (self.root / "human/private/condition_key.jsonl").read_text().splitlines()]
        self.assertTrue(any(set(k["conditions"]) == {"generic_1", "guided_1"} for k in keys))
        with self.assertRaises(ValueError):
            held_out_audit(self.root / "demo", self.root / "audit", "third-model")

    def test_existing_run_not_overwritten(self):
        RunStore(self.root / "run")
        with self.assertRaises(FileExistsError):
            RunStore(self.root / "run")


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = local_temp()
        self.addCleanup(self.temp.cleanup)
        self.store = RunStore(Path(self.temp.name) / "run")

    def client(self, response=None, error=None):
        calls = []

        def create(**kwargs):
            calls.append(kwargs)
            if error:
                raise error
            return response

        return SimpleNamespace(responses=SimpleNamespace(create=create)), calls

    def test_strict_schema_usage_and_storage_disabled(self):
        response = SimpleNamespace(status="completed", output_text='{"ok": true}', id="test", usage=SimpleNamespace(input_tokens=12, output_tokens=8))
        client, calls = self.client(response)
        budget = TokenBudget(10_000)
        adapter = OpenAIJSON("explicit-model", budget, self.store, client)
        self.assertEqual(adapter.generate("test", "instructions", {}, {"type": "object"}, 100), {"ok": True})
        self.assertEqual(budget.charged, 20)
        self.assertFalse(calls[0]["store"])
        self.assertTrue(calls[0]["text"]["format"]["strict"])

    def test_budget_prevents_network_call(self):
        client, calls = self.client()
        with self.assertRaises(BudgetExceeded):
            OpenAIJSON("model", TokenBudget(1), self.store, client).generate("test", "", {}, {}, 100)
        self.assertFalse(calls)

    def test_failures_charge_reservation_and_log(self):
        client, calls = self.client(error=RuntimeError("offline"))
        budget = TokenBudget(10_000)
        with self.assertRaises(RuntimeError):
            OpenAIJSON("model", budget, self.store, client).generate("test", "", {}, {}, 100)
        event = json.loads((self.store.directory / "events.jsonl").read_text())
        self.assertGreater(budget.charged, 100)
        self.assertEqual(event["usage_basis"], "reserved_unknown")

    def test_refusal_and_truncation_are_not_valid_responses(self):
        for index, response in enumerate((SimpleNamespace(status="incomplete", output_text='{"ok": true}', id="x"),
                                           SimpleNamespace(status="completed", output_text="", id="x"),
                                           SimpleNamespace(status="completed", output_text="bad-json", id="x"))):
            client, _ = self.client(response)
            with self.assertRaises(ValueError):
                OpenAIJSON("model", TokenBudget(10_000), self.store, client).generate("test", "", {}, {}, 100)


if __name__ == "__main__":
    unittest.main()
