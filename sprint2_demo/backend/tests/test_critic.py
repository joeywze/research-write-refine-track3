from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.writing.critic import (CriticError, QualitativeCritic, attach_critique,
                                guided_improvement, validate_critique)
from src.writing.contracts import digest
from src.writing.demo import FixtureProvider, fixture_inputs, remove_transitions
from src.writing.diagnostics import diagnose, targets
from src.writing.evaluation import held_out_audit, read_json
from src.writing.features import measure, measure_paragraph
from src.writing.pipeline import run_study
from src.writing.preservation import SemanticGate
from src.writing.prompts import CRITERIA
from src.writing.revision import apply_edits
from src.writing.storage import RunStore


def review(draft, actionable=(), status="ACTIONABLE"):
    return {"paragraphs": [{"paragraph_id": p.paragraph_id, "findings": [
        {"criterion": c, "status": status if (p.paragraph_id, c) in actionable else "NO_ISSUE",
         "quote": p.text[:30] if (p.paragraph_id, c) in actionable else "",
         "explanation": "Synthetic scripted judgement for control-flow testing.",
         "safe_action": "Clarify existing wording only." if (p.paragraph_id, c) in actionable and status == "ACTIONABLE" else ""}
        for c in CRITERIA]} for p in draft.paragraphs]}


class Scripted:
    test_only = True

    def __init__(self, responses, model="fixture-critic"):
        self.responses, self.calls, self.model = list(responses), [], model

    def generate(self, task, instructions, payload, schema, cap):
        self.calls.append((task, payload))
        raw = self.responses.pop(0)
        if isinstance(raw, Exception):
            raise raw
        return raw


class CriticTests(unittest.TestCase):
    def setUp(self):
        self.package, self.original, self.approved = fixture_inputs()
        self.quiet = replace(self.original, paragraphs=tuple(
            replace(p, text=remove_transitions(p.text)) for p in self.original.paragraphs))
        parent = Path(__file__).resolve().parents[1] / ".test-work"
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_measurements_do_not_change_score_or_targets(self):
        report = diagnose(self.quiet)
        self.assertEqual(report["score"], 0)
        self.assertFalse(targets(report))
        self.assertFalse(report["exploratory_measurements"]["affects_score_or_targets"])

    def test_measurement_counts_and_small_sample_nulls(self):
        data = measure_paragraph("This may work. This may work. It could fail.")
        self.assertEqual(data["repeated_trigrams"], {"this may work": 2})
        self.assertEqual(data["hedges"], {"may": 2, "could": 1})
        self.assertAlmostEqual(data["hedge_occurrences_per_100_words"], 100 / 3)
        self.assertIsNone(data["sentence_length_cv"])
        self.assertEqual(data["sentence_length_variance"], 0)
        self.assertIsNone(measure_paragraph("...")["hedge_occurrences_per_100_words"])
        self.assertIsNone(data["adjective_density"])

    def test_no_trigrams_cross_sentence_boundaries(self):
        self.assertEqual(measure_paragraph("One two. One two.")["repeated_trigrams"], {})

    def test_paragraph_regularity_requires_three_matched_section_paragraphs(self):
        report = measure(self.original)
        self.assertTrue(all(v["paragraph_length_cv"] is None for v in report["section_regularity"].values()))
        p = self.original.paragraphs[0]
        draft = replace(self.original, paragraphs=(p, replace(p, paragraph_id="extra_a"),
                                                  replace(p, paragraph_id="extra_b"), *self.original.paragraphs[1:]))
        self.assertEqual(measure(draft)["section_regularity"]["abstract"]["paragraph_length_cv"], 0)

    def test_complete_rubric_and_exact_quotes_required(self):
        raw = review(self.quiet, (("p_abstract", "specificity"),))
        valid = validate_critique(raw, self.quiet)
        self.assertEqual(valid["actionable_count"], 1)
        for mutation in ("missing_paragraph", "missing_criterion", "duplicate_criterion", "bad_quote", "no_action", "bad_status"):
            bad = deepcopy(raw)
            if mutation == "missing_paragraph":
                bad["paragraphs"].pop()
            elif mutation == "missing_criterion":
                bad["paragraphs"][0]["findings"].pop()
            elif mutation == "duplicate_criterion":
                bad["paragraphs"][0]["findings"][1] = bad["paragraphs"][0]["findings"][0]
            else:
                bad["paragraphs"][0]["findings"][0][{"bad_quote": "quote", "no_action": "safe_action",
                                                        "bad_status": "status"}[mutation]] = "" if mutation == "no_action" else "invented"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_critique(bad, self.quiet)

    def test_needs_research_is_saved_but_never_targeted(self):
        critique = validate_critique(review(self.quiet, (("p_abstract", "argument_strength"),), "NEEDS_RESEARCH"), self.quiet)
        self.assertFalse(targets(attach_critique(diagnose(self.quiet), critique)))
        raw = review(self.quiet)
        raw["paragraphs"][0]["findings"][0]["safe_action"] = "Add a result"
        with self.assertRaises(ValueError):
            validate_critique(raw, self.quiet)

    def test_bad_initial_critic_stops_before_either_rewrite(self):
        writer = Scripted([], "fixture-writer")
        gate = SemanticGate(FixtureProvider("fixture-auditor", [digest(self.quiet)]))
        for index, raw in enumerate((RuntimeError("offline"), {"paragraphs": []})):
            store = RunStore(self.root / f"bad_{index}")
            with self.assertRaises(CriticError):
                run_study(self.package, self.quiet, writer, gate,
                          {a: (writer, gate) for a in ("generic", "guided")}, store,
                          critic=QualitativeCritic(Scripted([raw])))
            self.assertFalse(writer.calls)

    def make_study(self, final_critique, name="study"):
        p = self.quiet.paragraphs[1]
        response = {"edits": [{"paragraph_id": p.paragraph_id,
                                "text": p.text.replace("The purpose is", "The aim is")} ]}
        candidate = apply_edits(self.quiet, response, (p.paragraph_id,))
        gate = SemanticGate(FixtureProvider("fixture-auditor", [digest(self.quiet), digest(candidate)]))
        initial = review(self.quiet, ((p.paragraph_id, "specificity"),))
        final = final_critique(candidate)
        if isinstance(final, dict) and "paragraphs" in final:
            final = {"paragraphs": [row for row in final["paragraphs"] if row["paragraph_id"] == p.paragraph_id]}
        provider = Scripted([initial, final])
        generic = Scripted([response], "fixture-writer")
        guided_response = {**response, "review_responses": [{
            "finding_id": "L:" + p.paragraph_id + ":specificity", "decision": "EDITED",
            "explanation": "Synthetic attempt to address the supplied wording finding.",
            "before_quote": "The purpose is", "after_quote": "The aim is"}]}
        guided = Scripted([guided_response], "fixture-writer")
        result = run_study(self.package, self.quiet, FixtureProvider("fixture-writer"), gate,
                           {"generic": (generic, gate), "guided": (guided, gate)}, RunStore(self.root / name),
                           critic=QualitativeCritic(provider))
        return result, generic, guided, provider, candidate

    def test_critic_targets_previously_unflagged_text_and_accepts_safe_improvement(self):
        result, generic, guided, provider, candidate = self.make_study(review)
        self.assertEqual(result["results"]["guided"]["stop_reason"], "NO_ACTIONABLE_DIAGNOSTICS")
        self.assertTrue(result["results"]["guided"]["attempts"][0]["accepted"])
        self.assertEqual(generic.calls[0][1]["allowed_paragraph_ids"], guided.calls[0][1]["allowed_paragraph_ids"])
        self.assertNotIn("diagnostics", generic.calls[0][1])
        self.assertIn("qualitative_critic", guided.calls[0][1]["diagnostics"])
        self.assertNotIn("exploratory_measurements", guided.calls[0][1]["diagnostics"])
        self.assertNotIn("diagnostics", provider.calls[-1][1])
        self.assertEqual(result["results"]["guided"]["final_diagnostics"]["score"], 0)

    def test_candidate_critic_error_rolls_back(self):
        result, *_ = self.make_study(lambda draft: {"paragraphs": []})
        guided = result["results"]["guided"]
        self.assertEqual(guided["stop_reason"], "CRITIC_ERROR")
        self.assertEqual(guided["final_hash"], digest(self.quiet))
        self.assertTrue((self.root / "study/guided_1_critic_response.json").exists())

    def test_uncertainty_does_not_masquerade_as_resolved_style_issue(self):
        for index, status in enumerate(("INSUFFICIENT_EVIDENCE", "NEEDS_RESEARCH")):
            result, *_ = self.make_study(lambda d: review(d, (("p_introduction", "specificity"),), status), f"uncertain_{index}")
            self.assertEqual(result["results"]["guided"]["stop_reason"], "INSUFFICIENT_IMPROVEMENT")

    def test_surface_improvement_cannot_hide_more_critic_issues(self):
        before = attach_critique(diagnose(self.original), validate_critique(review(self.original), self.original))
        after = attach_critique(diagnose(self.quiet), validate_critique(
            review(self.quiet, (("p_abstract", "specificity"),)), self.quiet))
        self.assertLess(after["score"], before["score"])
        self.assertFalse(guided_improvement(before, after, 1))

    def test_deferred_style_criterion_does_not_erase_a_surface_problem(self):
        before = attach_critique(diagnose(self.original), validate_critique(review(self.original), self.original))
        shortened = replace(self.original, paragraphs=tuple(replace(p, text="Short text.") for p in self.original.paragraphs))
        after = attach_critique(diagnose(shortened), validate_critique(review(shortened), shortened))
        self.assertFalse(guided_improvement(before, after, 1))

    def test_held_out_evaluator_cannot_reuse_style_critic(self):
        store = RunStore(self.root / "audit_input")
        store.write("configuration.json", {"test_only": False, "writer_model": "writer",
                                           "preservation_model": "checker", "critic_model": "critic"})
        with self.assertRaisesRegex(ValueError, "optional style critic"):
            held_out_audit(store.directory, self.root / "audit", "CRITIC")

    def test_offline_measure_command_saves_unscored_measurements(self):
        from src.writing.__main__ import main
        package = self.root / "input"
        store = RunStore(package)
        store.write("package.json", self.package)
        store.write("v0.json", self.quiet)
        output = self.root / "measurement"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["measure", "--package", str(package / "package.json"),
                                   "--v0", str(package / "v0.json"), "--output", str(output)]), 0)
        result = read_json(output / "diagnostics.json")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["exploratory_measurements"]["status"], "MEASUREMENT_ONLY_UNCALIBRATED")

    def test_writer_cannot_be_reused_as_style_critic(self):
        writer = FixtureProvider("fixture-writer")
        gate = SemanticGate(FixtureProvider("fixture-auditor", self.approved))
        with self.assertRaisesRegex(ValueError, "separate preservation model"):
            run_study(self.package, self.original, writer, gate,
                      {a: (writer, gate) for a in ("generic", "guided")}, RunStore(self.root / "same"),
                      critic=QualitativeCritic(Scripted([], "fixture-writer")))

    def invoke_run(self, name, extra=()):
        from src.writing.__main__ import main
        inputs = RunStore(self.root / (name + "_inputs"))
        inputs.write("package.json", self.package)
        inputs.write("v0.json", self.quiet)
        output = self.root / name
        calls = []

        def provider(model, budget, store, stage):
            calls.append((model, stage))
            return FixtureProvider(model)

        args = ["run", "--package", str(inputs.directory / "package.json"),
                "--v0", str(inputs.directory / "v0.json"), "--writer-model", "writer",
                "--checker-model", "checker", "--output", str(output), *extra]
        with patch("src.writing.__main__.OpenAIJSON", side_effect=provider), \
                patch("src.writing.__main__.run_study", return_value={}) as study, \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = main(args)
        return code, study, calls, output

    def test_live_command_defaults_to_rules_and_critic(self):
        code, study, calls, output = self.invoke_run("default_method")
        self.assertEqual(code, 0)
        self.assertEqual(study.call_args.kwargs["critic"].model, "checker")
        self.assertIn(("checker", "critique"), calls)
        self.assertEqual(read_json(output / "budget_configuration.json")["max_stage_or_arm_count"], 4)

    def test_explicit_critic_model_overrides_checker_default(self):
        _, study, calls, _ = self.invoke_run("custom_critic", ("--critic-model", "style-model"))
        self.assertEqual(study.call_args.kwargs["critic"].model, "style-model")
        self.assertIn(("style-model", "critique"), calls)

    def test_rules_only_requires_explicit_selection(self):
        _, study, calls, output = self.invoke_run("rules_baseline", ("--method", "rules-only"))
        self.assertIsNone(study.call_args.kwargs["critic"])
        self.assertFalse(any(stage == "critique" for _, stage in calls))
        self.assertEqual(read_json(output / "budget_configuration.json")["max_stage_or_arm_count"], 3)

    def test_conflicting_method_options_are_not_silently_ignored(self):
        with self.assertRaises(SystemExit):
            self.invoke_run("conflicting", ("--method", "rules-only", "--critic-model", "style-model"))
        self.assertFalse((self.root / "conflicting").exists())

    def test_default_method_rejects_invalid_critic_before_calls(self):
        for index, model in enumerate(("", "writer")):
            with self.assertRaises(SystemExit):
                self.invoke_run(f"bad_model_{index}", ("--critic-model", model))
            self.assertFalse((self.root / f"bad_model_{index}").exists())

    def test_score_labels_describe_the_count_sources(self):
        self.assertEqual(diagnose(self.quiet)["score_label"], "Review points flagged by rules")
        critique = validate_critique(review(self.quiet), self.quiet)
        self.assertEqual(critique["score_label"], "Review points flagged by the LLM")


if __name__ == "__main__":
    unittest.main()
