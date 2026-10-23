"""Review passages for clearer, more precise, better-connected or more natural wording."""

from dataclasses import asdict

from .contracts import digest, fields, text
from .prompts import CRITIC_INSTRUCTIONS, CRITIC_SCHEMA, CRITERIA, CRITIC_STATUSES
from .providers import BudgetExceeded

CRITIC_VERSION = "rubric-0.1"


class CriticError(ValueError):
    pass


class QualitativeCritic:
    def __init__(self, provider, max_output_tokens=6000):
        self.provider = provider
        self.model = provider.model
        self.test_only = provider.test_only
        self.max_output_tokens = max_output_tokens

    def assess(self, package, draft, label, store):
        payload = {"package": asdict(package), "draft": asdict(draft),
                   "draft_hash": digest(draft), "criteria": list(CRITERIA)}
        try:
            raw = self.provider.generate("style_critic_" + label, CRITIC_INSTRUCTIONS,
                                         payload, CRITIC_SCHEMA, self.max_output_tokens)
            store.write(label + "_critic_response.json", raw)
            report = validate_critique(raw, draft)
            store.write(label + "_critic.json", report)
            return report
        except BudgetExceeded:
            raise
        except OSError:
            raise
        except Exception as error:
            store.event("critic_failed", label=label, draft_hash=digest(draft),
                        error_type=type(error).__name__, message=str(error))
            raise CriticError(f"Could not obtain a valid style critique: {error}") from error


def validate_critique(raw, draft):
    fields(raw, {"paragraphs"}, "style critique")
    if not isinstance(raw["paragraphs"], list):
        raise ValueError("Critique paragraphs must be a list")
    expected = {p.paragraph_id: p for p in draft.paragraphs}
    seen, output = set(), []
    for paragraph in raw["paragraphs"]:
        fields(paragraph, {"paragraph_id", "findings"}, "paragraph critique")
        pid = paragraph["paragraph_id"]
        if pid not in expected or pid in seen or not isinstance(paragraph["findings"], list):
            raise ValueError("Unknown/duplicate paragraph or invalid findings")
        seen.add(pid)
        criteria = set()
        findings = []
        for finding in paragraph["findings"]:
            fields(finding, {"criterion", "status", "quote", "explanation", "safe_action"}, "finding")
            criterion, status = finding["criterion"], finding["status"]
            if criterion not in CRITERIA or criterion in criteria or status not in CRITIC_STATUSES:
                raise ValueError("Unknown/duplicate criterion or invalid status")
            criteria.add(criterion)
            for key in ("quote", "explanation", "safe_action"):
                if not isinstance(finding[key], str):
                    raise ValueError("Critic finding fields must be strings")
            text(finding["explanation"], "finding explanation")
            if finding["quote"] and finding["quote"] not in expected[pid].text:
                raise ValueError("Critic quote is absent from its paragraph")
            if status == "ACTIONABLE":
                text(finding["quote"], "actionable quote")
                text(finding["safe_action"], "safe action")
            elif finding["safe_action"].strip():
                raise ValueError("Only actionable findings may instruct a rewrite")
            findings.append(dict(finding))
        if criteria != set(CRITERIA):
            raise ValueError("Every rubric criterion must be assessed for every paragraph")
        output.append({"paragraph_id": pid, "findings": findings})
    if seen != set(expected):
        raise ValueError("Critic omitted paragraphs")
    by_id = {p["paragraph_id"]: p for p in output}
    ordered = [by_id[p.paragraph_id] for p in draft.paragraphs]
    return {"version": CRITIC_VERSION, "status": "COMPLETE", "draft_hash": digest(draft),
            "score_label": "Review points flagged by the LLM",
            "interpretation": "Passages that could benefit from clearer, more precise, better-connected or more natural wording. Independent assessment is needed to evaluate the suggestions.",
            "actionable_count": sum(f["status"] == "ACTIONABLE" for p in ordered for f in p["findings"]),
            "paragraphs": ordered}


def attach_critique(report, critique):
    return {**report, "qualitative_critic": critique}


def guided_improvement(before, after, minimum):
    """Require one count to fall and neither to rise when the critic is used."""
    old, new = before.get("qualitative_critic"), after.get("qualitative_critic")
    if old is None and new is None:
        return before["score"] is not None and after["score"] is not None and before["score"] - after["score"] >= minimum
    if old is None or new is None:
        return False
    old_findings = {(p["paragraph_id"], f["criterion"]): f["status"]
                    for p in old["paragraphs"] for f in p["findings"]}
    for p in new["paragraphs"]:
        for f in p["findings"]:
            previous = old_findings[(p["paragraph_id"], f["criterion"])]
            if (f["status"] == "NEEDS_RESEARCH" and previous != "NEEDS_RESEARCH") or (
                    previous == "ACTIONABLE" and f["status"] not in {"ACTIONABLE", "NO_ISSUE"}):
                return False
    # Becoming too short to score cannot count as fixing an issue.
    old_eligible = {p["paragraph_id"] for p in before["paragraphs"] if p["applicable"]}
    new_eligible = {p["paragraph_id"] for p in after["paragraphs"] if p["applicable"]}
    if not old_eligible <= new_eligible:
        return False
    surface_delta = (before["score"] or 0) - (after["score"] or 0)
    critic_delta = old["actionable_count"] - new["actionable_count"]
    return surface_delta >= 0 and critic_delta >= 0 and max(surface_delta, critic_delta) >= minimum
