"""Revise selected paragraphs and retain the last draft that passes the checks."""

from dataclasses import asdict, dataclass
import csv
import json
from time import perf_counter

from .contracts import Draft, ResearchPackage, digest
from .critic import CriticError, attach_critique, guided_improvement
from .diagnostics import DiagnosticConfig, diagnose, targets
from .prompts import DRAFT_INSTRUCTIONS, DRAFT_SCHEMA, PROMPT_VERSION
from .providers import BudgetExceeded
from .revision import apply_edits
from .prompts import EDIT_SCHEMA, GENERIC_INSTRUCTIONS, GUIDED_INSTRUCTIONS


@dataclass(frozen=True)
class RunConfig:
    max_attempts: int = 3
    min_improvement: float = 1.0
    max_output_tokens: int = 6000
    diagnostics: DiagnosticConfig = DiagnosticConfig()

    def __post_init__(self):
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 3:
            raise ValueError("At most three revision attempts per draft")
        if not 0 < self.min_improvement < float("inf"):
            raise ValueError("min_improvement must be finite and positive")
        if type(self.max_output_tokens) is not int or self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")


def require_independent(writer, gate):
    if writer.model.strip().casefold() == gate.model.strip().casefold():
        raise ValueError("Choose a separate preservation model or style critic model")
    if writer.test_only != gate.test_only:
        raise ValueError("Cannot mix fixture-only and live providers")


def create_v0(package: ResearchPackage, writer, store, config: RunConfig) -> Draft:
    response = writer.generate("draft_v0", DRAFT_INSTRUCTIONS, {"package": asdict(package)},
                               DRAFT_SCHEMA, config.max_output_tokens)
    store.write("v0_generation_response.json", response)
    # Check the draft format before the package-based content check.
    return Draft.from_dict(response, package)


def run_arm(package, v0, writer, gate, store, arm, config, initial_targets,
            initial_report=None, critic=None):
    accepted = v0
    report = initial_report if initial_report is not None else diagnose(accepted, config.diagnostics)
    previous_candidates = {digest(v0)}
    attempts = []
    stop = "MAX_ATTEMPTS"
    maximum = 1 if arm == "generic" else config.max_attempts
    for number in range(1, maximum + 1):
        allowed = initial_targets if number == 1 else targets(report)
        if not allowed:
            stop = "NO_ACTIONABLE_DIAGNOSTICS"
            break
        start = perf_counter()
        record = {"arm": arm, "attempt": number, "allowed_paragraph_ids": list(allowed),
                  "parent_hash": digest(accepted), "v0_hash": digest(v0),
                  "score_before": report["score"], "score_after": None,
                  "accepted": False, "preservation": None}
        record["critic_count_before"] = report.get("qualitative_critic", {}).get("actionable_count")
        record["critic_count_after"] = None
        prefix = f"{arm}_{number}"
        payload = {"package": asdict(package), "draft": asdict(accepted),
                   "allowed_paragraph_ids": list(allowed)}
        if arm == "guided":
            payload["diagnostics"] = {**report, "paragraphs": [p for p in report["paragraphs"]
                                                              if p["paragraph_id"] in allowed]}
            # Save measurements for analysis without passing them as edit instructions.
            payload["diagnostics"].pop("exploratory_measurements", None)
            if "qualitative_critic" in report:
                payload["diagnostics"]["qualitative_critic"] = {
                    **report["qualitative_critic"], "paragraphs": [
                        {**p, "findings": [f for f in p["findings"] if f["status"] == "ACTIONABLE"]}
                        for p in report["qualitative_critic"]["paragraphs"] if p["paragraph_id"] in allowed]}
        try:
            raw = writer.generate("revision_" + arm,
                                  GUIDED_INSTRUCTIONS if arm == "guided" else GENERIC_INSTRUCTIONS,
                                  payload, EDIT_SCHEMA, config.max_output_tokens)
            # Retain invalid responses and rejected candidates for inspection.
            store.write(prefix + "_response.json", raw)
            candidate = apply_edits(accepted, raw, tuple(allowed))
            store.write(prefix + "_candidate.json", candidate)
            candidate_hash = digest(candidate)
            record["candidate_hash"] = candidate_hash
            if candidate_hash in previous_candidates:
                record["score_after"] = diagnose(candidate, config.diagnostics)["score"]
                record["reason"] = "UNCHANGED_OR_REPEATED"
                stop = record["reason"]
            else:
                previous_candidates.add(candidate_hash)
                candidate_report = diagnose(candidate, config.diagnostics)
                record["score_after"] = candidate_report["score"]
                preservation = gate.check(package, candidate, (v0, accepted))
                store.write(prefix + "_preservation.json", preservation)
                record["preservation"] = asdict(preservation)
                if preservation.status == "PASS" and arm == "guided" and critic is not None:
                    critique = critic.assess(package, candidate, prefix, store)
                    candidate_report = attach_critique(candidate_report, critique)
                    record["critic_count_after"] = critique["actionable_count"]
                store.write(prefix + "_diagnostics.json", candidate_report)
                if preservation.status != "PASS":
                    record["reason"] = preservation.status
                    stop = "PRESERVATION_FAILED"
                elif arm == "generic":
                    # Generic acceptance depends on preservation alone.
                    record["accepted"] = True
                    record["reason"] = "PRESERVED_GENERIC_REWRITE"
                elif not guided_improvement(report, candidate_report, config.min_improvement):
                    record["reason"] = "INSUFFICIENT_IMPROVEMENT"
                    stop = record["reason"]
                else:
                    record["accepted"] = True
                    record["reason"] = "PRESERVED_AND_IMPROVED"
                if record["accepted"]:
                    # Save the accepted draft before starting another attempt.
                    store.write(prefix + "_accepted.json", candidate)
                    accepted = candidate
                    report = candidate_report
        except CriticError as error:
            record["reason"] = "CRITIC_ERROR"
            record["error"] = str(error)
            stop = record["reason"]
        except BudgetExceeded as error:
            record["reason"] = "BUDGET_EXHAUSTED"
            record["error"] = str(error)
            stop = record["reason"]
        except (ValueError, TypeError, KeyError) as error:
            record["reason"] = "INVALID_RESPONSE"
            record["error"] = f"{type(error).__name__}: {error}"
            stop = record["reason"]
        except OSError:
            # Stop if the run can no longer save its results.
            raise
        except Exception as error:
            record["reason"] = "MODEL_ERROR"
            record["error"] = f"{type(error).__name__}: {error}"
            stop = record["reason"]
        record["elapsed_seconds"] = perf_counter() - start
        record["last_accepted_hash"] = digest(accepted)
        store.write(prefix + "_attempt.json", record)
        store.event("revision_attempt", **record)
        attempts.append(record)
        # Stop after a failed attempt; it still counts towards the limit.
        if not record["accepted"]:
            break
        if arm == "guided" and not targets(report):
            stop = "NO_ACTIONABLE_DIAGNOSTICS"
            break
    store.write(arm + "_final.json", accepted)
    (store.directory / (arm + "_final.md")).write_text(accepted.markdown(package), encoding="utf-8")
    result = {"arm": arm, "stop_reason": stop, "attempts": attempts,
              "final_hash": digest(accepted), "final_diagnostics": report}
    store.write(arm + "_summary.json", result)
    return result


def run_study(package, v0, baseline_writer, baseline_gate, arms, store, config=RunConfig(), critic=None):
    """Compare generic and guided revision of one six-section draft.

    Match the writer model, initial paragraph scope and per-call output cap.
    Each version has an equal writing and preservation allowance. Record the
    critic's calls separately and distinguish first attempts from later ones.
    """
    if set(arms) != {"generic", "guided"}:
        raise ValueError("Both generic and guided arms are required")
    require_independent(baseline_writer, baseline_gate)
    if critic is not None:
        require_independent(baseline_writer, critic)
    for writer, gate in arms.values():
        require_independent(writer, gate)
        if (writer.model, gate.model, writer.test_only) != (
                baseline_writer.model, baseline_gate.model, baseline_writer.test_only):
            raise ValueError("Both arms must use the same writer and preservation model configuration")
    store.write("package.json", package)
    store.write("configuration.json", {"run": asdict(config), "prompt_version": PROMPT_VERSION,
                                       "writer_model": baseline_writer.model,
                                       "preservation_model": baseline_gate.model,
                                        "critic_model": critic.model if critic else None,
                                        "method": "rules-critic" if critic else "rules-only",
                                        "acceptance_rule": "surface_and_critic_no_regression" if critic else "surface_only",
                                       "test_only": baseline_writer.test_only,
                                       "package_hash": digest(package)})
    if v0 is None:
        v0 = create_v0(package, baseline_writer, store, config)
    store.write("v0_input.json", v0)
    grounding = baseline_gate.check(package, v0)
    store.write("v0_preservation.json", grounding)
    store.event("v0_gate", status=grounding.status, reasons=list(grounding.reasons), v0_hash=digest(v0))
    if grounding.status != "PASS":
        store.write("study_summary.json", {"status": "V0_REJECTED", "reasons": list(grounding.reasons)})
        raise ValueError("V0 failed grounding; see v0_preservation.json")
    store.write("v0_accepted.json", v0)
    (store.directory / "v0.md").write_text(v0.markdown(package), encoding="utf-8")
    report = diagnose(v0, config.diagnostics)
    if critic is not None:
        report = attach_critique(report, critic.assess(package, v0, "v0", store))
    store.write("v0_diagnostics.json", report)
    initial_targets = targets(report)
    results = {arm: run_arm(package, v0, *arms[arm], store, arm, config, initial_targets,
                           initial_report=report, critic=critic if arm == "guided" else None)
               for arm in ("generic", "guided")}
    columns = ["arm", "attempt", "score_before", "candidate_score", "accepted_score", "accepted", "reason",
               "critic_count_before", "candidate_critic_count", "accepted_critic_count"]
    with (store.directory / "trajectory.csv").open("x", encoding="utf-8", newline="") as handle:
        trace = csv.DictWriter(handle, fieldnames=columns)
        trace.writeheader()
        for arm, result in results.items():
            trace.writerow({"arm": arm, "attempt": 0, "candidate_score": report["score"],
                            "accepted_score": report["score"], "accepted": True, "reason": "GROUNDED_V0",
                            "candidate_critic_count": report.get("qualitative_critic", {}).get("actionable_count"),
                            "accepted_critic_count": report.get("qualitative_critic", {}).get("actionable_count")})
            for attempt in result["attempts"]:
                trace.writerow({"arm": arm, "attempt": attempt["attempt"],
                                "score_before": attempt["score_before"], "candidate_score": attempt["score_after"],
                                "accepted_score": attempt["score_after"] if attempt["accepted"] else attempt["score_before"],
                                "accepted": attempt["accepted"], "reason": attempt["reason"],
                                "critic_count_before": attempt["critic_count_before"],
                                "candidate_critic_count": attempt["critic_count_after"],
                                "accepted_critic_count": (attempt["critic_count_after"] if attempt["accepted"]
                                                          else attempt["critic_count_before"])})
    calls = [json.loads(line) for line in (store.directory / "events.jsonl").read_text(encoding="utf-8").splitlines()
             if json.loads(line)["kind"] == "model_call"]
    costs = {}
    for stage in ("v0", "generic", "guided", "critique"):
        stage_calls = [call for call in calls if call["stage"] == stage]
        known = [call for call in stage_calls if call["usage"] is not None]
        costs[stage] = {"model_calls": len(stage_calls), "usage_unknown_calls": len(stage_calls) - len(known),
                        "reported_input_tokens": sum(c["usage"]["input_tokens"] for c in known) if known else None,
                        "reported_output_tokens": sum(c["usage"]["output_tokens"] for c in known) if known else None,
                        "charged_tokens": stage_calls[-1]["charged_tokens"] if stage_calls else None,
                        "elapsed_model_seconds": sum(c["elapsed_seconds"] for c in stage_calls) if stage_calls else None}
    store.write("cost_summary.json", {"test_only": baseline_writer.test_only, "stages": costs,
                                      "critique_cost_note": "Includes the initial critique and assessments of guided candidates.",
                                      "monetary_cost": "NOT_ESTIMATED"})
    summary = {"status": "COMPLETED", "test_only": baseline_writer.test_only,
               "package_hash": digest(package), "v0_hash": digest(v0), "v0_score": report["score"],
               "score_direction": "lower_is_better", "results": results,
               "method": "rules-critic" if critic else "rules-only",
               "score_labels": {"surface": "Review points flagged by rules", "critic": "Review points flagged by the LLM"},
               "evaluation_status": "PENDING_HUMAN_AND_HELD_OUT_PRESERVATION",
               "final_comparison": "Compare final guided V2 with final generic V1 and report the extra calls.",
               "comparison": "First attempts compare feedback on the same initial paragraphs; later guided attempts add computation."}
    store.write("study_summary.json", summary)
    return summary
