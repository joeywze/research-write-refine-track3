"""Review passages for clearer, more precise, better-connected or more natural wording."""

from dataclasses import asdict

from .contracts import digest, fields, text
from .prompts import (
    CRITIC_INSTRUCTIONS, CRITIC_SCHEMA, CRITERIA, CRITIC_STATUSES, FINDING_FIELDS, STRING, array, obj,
)
from .providers import BudgetExceeded

CRITIC_VERSION = "rubric-0.2-changed-paragraphs"
CONTEXT_CRITIC_VERSION = "rubric-0.3-section-review"
CONTEXT_SCHEMA = obj({"paragraphs": array(obj({"paragraph_id": STRING, "findings": array(obj({
    **FINDING_FIELDS, "related_paragraph_id": STRING, "related_quote": STRING,
}))}))})
SECTION_REVIEW = """
Use detector hints as leads. An unusual pattern alone does not justify an edit.
Check whether the abstract and conclusion describe the same contribution,
whether the experiments address the stated research questions, and whether
repeated material serves a distinct purpose in each section. Use the existing
rubric criteria for these findings. For a cross-section finding, quote the
target passage and provide the ID and exact quote of a passage in another
section. Leave both related fields empty for local findings.
Only paragraphs in editable_paragraph_ids can receive ACTIONABLE findings.
For a conflict that requires a new claim, evidence or design, use NEEDS_RESEARCH.
"""


class CriticError(ValueError):
    pass


class QualitativeCritic:
    def __init__(self, provider, max_output_tokens=6000, *, detector_hints=None, editable_ids=()):
        self.provider = provider
        self.model = provider.model
        self.test_only = provider.test_only
        self.max_output_tokens = max_output_tokens
        self.detector_hints = detector_hints
        self.editable_ids = tuple(editable_ids)
        self.instructions = CRITIC_INSTRUCTIONS if detector_hints is None else CRITIC_INSTRUCTIONS + SECTION_REVIEW
        self.schema = CRITIC_SCHEMA if detector_hints is None else CONTEXT_SCHEMA
        self.version = CRITIC_VERSION if detector_hints is None else CONTEXT_CRITIC_VERSION

    def configuration(self):
        return {"model": self.model, "instructions_hash": digest(self.instructions),
                "schema_hash": digest(self.schema), "max_output_tokens": self.max_output_tokens}

    def assess(self, package, draft, label, store, *, previous_draft=None, previous_critique=None):
        try:
            if (previous_draft is None) != (previous_critique is None):
                raise ValueError("Previous draft and critique must be supplied together")
            previous = {}
            retained = []
            if previous_draft is not None:
                if previous_critique["draft_hash"] != digest(previous_draft):
                    raise ValueError("Previous critique does not match its draft")
                if previous_critique.get("package_hash") != digest(package):
                    raise ValueError("Previous critique does not match this research package")
                if previous_critique["version"] != self.version:
                    raise ValueError("Do not reuse findings from another critic version")
                if previous_critique.get("assessment_configuration") != self.configuration():
                    raise ValueError("Do not reuse findings from another critic configuration")
                identity = lambda d: [(p.paragraph_id, p.section, p.claim_ids) for p in d.paragraphs]
                if identity(previous_draft) != identity(draft):
                    raise ValueError("Paragraph identities changed between assessments")
                previous = {p.paragraph_id: p for p in previous_draft.paragraphs}
                # Validate the retained rows as well as the new response.
                validate_critique({"paragraphs": previous_critique["paragraphs"]}, previous_draft,
                                  editable_ids=self.editable_ids if self.detector_hints is not None else None)
                if self.detector_hints is None:
                    retained = [p.paragraph_id for p in draft.paragraphs if p.text == previous[p.paragraph_id].text]
            requested = [p.paragraph_id for p in draft.paragraphs if p.paragraph_id not in retained]
            payload = {"package": asdict(package), "draft": asdict(draft),
                       "draft_hash": digest(draft), "criteria": list(CRITERIA),
                       "paragraph_ids_to_assess": requested}
            if self.detector_hints is not None:
                payload["detector_hints"] = self.detector_hints(draft)
                payload["editable_paragraph_ids"] = list(self.editable_ids)
                store.write(label + "_detector_hints.json", payload["detector_hints"])
            if previous:
                payload["previous_paragraphs"] = [asdict(previous[pid]) for pid in requested]
                payload["previous_assessment"] = {"draft_hash": previous_critique["draft_hash"],
                    "paragraphs": [p for p in previous_critique["paragraphs"] if p["paragraph_id"] in requested]}
            raw = (self.provider.generate("style_critic_" + label, self.instructions,
                                         payload, self.schema, self.max_output_tokens)
                   if requested else {"paragraphs": []})
            store.write(label + "_critic_response.json", raw)
            editable_ids = self.editable_ids if self.detector_hints is not None else None
            partial = validate_critique(raw, draft, expected_ids=requested, editable_ids=editable_ids)
            old_rows = previous_critique["paragraphs"] if previous_critique else []
            merged = partial["paragraphs"] + [p for p in old_rows if p["paragraph_id"] in retained]
            report = validate_critique({"paragraphs": merged}, draft, editable_ids=editable_ids)
            report["package_hash"] = digest(package)
            report["assessment_configuration"] = self.configuration()
            mode = "whole_draft_section_review" if self.detector_hints is not None else (
                "changed_paragraphs" if previous else "initial_full_review")
            report["assessment_scope"] = {"mode": mode,
                "reassessed_paragraph_ids": requested, "retained_paragraph_ids": retained,
                "parent_draft_hash": digest(previous_draft) if previous_draft is not None else None,
                "model_call_made": bool(requested),
                "limitation": ("The critic reassesses all sections. Independent ratings are needed to assess quality."
                               if self.detector_hints is not None else
                               "Unchanged paragraph findings are retained. Context-dependent style effects outside changed paragraphs need separate validation; semantic preservation still covers the whole document.")}
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


def validate_critique(raw, draft, expected_ids=None, *, editable_ids=None):
    fields(raw, {"paragraphs"}, "style critique")
    if not isinstance(raw["paragraphs"], list):
        raise ValueError("Critique paragraphs must be a list")
    all_paragraphs = {p.paragraph_id: p for p in draft.paragraphs}
    requested = set(all_paragraphs) if expected_ids is None else set(expected_ids)
    if not requested <= set(all_paragraphs):
        raise ValueError("Unknown requested paragraph")
    expected = {pid: all_paragraphs[pid] for pid in requested}
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
            finding_fields = set(FINDING_FIELDS)
            if editable_ids is not None:
                finding_fields.update(("related_paragraph_id", "related_quote"))
            fields(finding, finding_fields, "finding")
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
                if editable_ids is not None and pid not in editable_ids:
                    raise ValueError("Critic targeted a locked or non-prose paragraph")
                text(finding["quote"], "actionable quote")
                text(finding["safe_action"], "safe action")
            elif finding["safe_action"].strip():
                raise ValueError("Only actionable findings may instruct a rewrite")
            if editable_ids is not None:
                related_id, quote = finding["related_paragraph_id"], finding["related_quote"]
                if not isinstance(related_id, str) or not isinstance(quote, str) or bool(related_id) != bool(quote):
                    raise ValueError("Cross-section evidence needs both a paragraph ID and a quote")
                if related_id:
                    related = all_paragraphs.get(related_id)
                    text(finding["quote"], "target passage quote")
                    text(quote, "related passage quote")
                    if related is None or related.section == expected[pid].section or quote not in related.text:
                        raise ValueError("Cross-section quote must match a passage in a different section")
            findings.append(dict(finding))
        if criteria != set(CRITERIA):
            raise ValueError("Every rubric criterion must be assessed for every paragraph")
        output.append({"paragraph_id": pid, "findings": findings})
    if seen != set(expected):
        raise ValueError("Critic omitted paragraphs")
    by_id = {p["paragraph_id"]: p for p in output}
    ordered = [by_id[p.paragraph_id] for p in draft.paragraphs if p.paragraph_id in requested]
    version = CRITIC_VERSION if editable_ids is None else CONTEXT_CRITIC_VERSION
    return {"version": version, "status": "COMPLETE", "draft_hash": digest(draft),
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
    resolved_review_point = False
    for p in new["paragraphs"]:
        for f in p["findings"]:
            previous = old_findings[(p["paragraph_id"], f["criterion"])]
            if previous == "ACTIONABLE" and f["status"] == "NO_ISSUE":
                resolved_review_point = True
            if (f["status"] == "NEEDS_RESEARCH" and previous != "NEEDS_RESEARCH") or (
                    previous == "ACTIONABLE" and f["status"] not in {"ACTIONABLE", "NO_ISSUE"}):
                return False
    if old.get("version") == CONTEXT_CRITIC_VERSION and not resolved_review_point:
        return False
    # Becoming too short to score cannot count as fixing an issue.
    old_eligible = {p["paragraph_id"] for p in before["paragraphs"] if p["applicable"]}
    new_eligible = {p["paragraph_id"] for p in after["paragraphs"] if p["applicable"]}
    if not old_eligible <= new_eligible:
        return False
    surface_delta = (before["score"] or 0) - (after["score"] or 0)
    critic_delta = old["actionable_count"] - new["actionable_count"]
    return surface_delta >= 0 and critic_delta >= 0 and max(surface_delta, critic_delta) >= minimum
