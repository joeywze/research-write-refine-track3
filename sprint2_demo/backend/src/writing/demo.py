"""Scripted responses for testing the workflow with synthetic research data."""

from dataclasses import asdict
from pathlib import Path
import re

from .contracts import Draft, ResearchPackage, digest
from .evaluation import read_json
from .pipeline import RunConfig, run_study
from .preservation import SemanticGate
from .revision import apply_edits
from .storage import RunStore


def remove_transitions(prose):
    # Keep sentence capitals when removing a transition.
    return re.sub(r"(^|[.!?]\s+)(?:Moreover|Furthermore),\s+([A-Za-z])",
                  lambda match: match[1] + match[2].upper(), prose)


class FixtureProvider:
    test_only = True

    def __init__(self, model, approved_hashes=()):
        self.model = model
        self.approved_hashes = set(approved_hashes)

    def generate(self, task, instructions, payload, schema, max_output_tokens):
        if task == "preservation":
            if payload["candidate_hash"] not in self.approved_hashes:
                raise ValueError("No pre-approved synthetic audit fixture for this exact candidate")
            return {"global_status": "PASS", "global_reasons": [],
                    "paragraphs": [{"paragraph_id": p["paragraph_id"], "status": "PASS",
                                    "checked_claim_ids": p["claim_ids"], "reasons": []}
                                   for p in payload["candidate"]["paragraphs"]]}
        if task.startswith("revision_"):
            first = payload["allowed_paragraph_ids"][0]
            p = next(p for p in payload["draft"]["paragraphs"] if p["paragraph_id"] == first)
            return {"edits": [{"paragraph_id": first, "text": remove_transitions(p["text"])}]}
        raise ValueError("Unsupported fixture task")


def fixture_inputs():
    root = Path(__file__).resolve().parents[2]
    package = ResearchPackage.from_dict(read_json(root / "examples/research_package.json"))
    v0 = Draft.from_dict(read_json(root / "examples/v0.json"), package)
    approved = [digest(v0)]
    draft = v0
    for p in v0.paragraphs:
        draft = apply_edits(draft, {"edits": [{"paragraph_id": p.paragraph_id,
                                               "text": remove_transitions(p.text)}]}, (p.paragraph_id,))
        approved.append(digest(draft))
    return package, v0, approved


def run_demo(output):
    package, v0, approved = fixture_inputs()
    store = RunStore(output)

    def pair():
        return FixtureProvider("fixture-writer"), SemanticGate(FixtureProvider("fixture-auditor", approved))

    writer, gate = pair()
    summary = run_study(package, v0, writer, gate, {a: pair() for a in ("generic", "guided")},
                        store, RunConfig())
    return {"test_only": True, "interpretation": "Offline example using scripted responses and synthetic data.",
            "v0_score": summary["v0_score"],
            "guided_scores": [a["score_after"] for a in summary["results"]["guided"]["attempts"]],
            "stop_reason": summary["results"]["guided"]["stop_reason"], "output": str(Path(output).resolve())}
