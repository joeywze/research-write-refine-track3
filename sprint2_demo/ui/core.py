"""Read real run evidence and exercise the existing preservation code."""
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from difflib import SequenceMatcher
from pathlib import Path
import json
import re
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from handover import Draft, ResearchPackage, LockedTablesGate, render, read
from run_live import RATES
from src.writing.contracts import CITATION, digest
from src.writing.diagnostics import diagnose
from src.writing.pipeline import RunConfig, run_arm
from src.writing.preservation import SemanticGate
from src.writing.storage import RunStore
from project_io import validate_upload

DEFAULT_RUN = "live-20261026T000828046240Z"
SECTIONS = {"abstract": "Abstract", "introduction": "Introduction", "related_work": "Related work",
            "methodology": "Methodology", "experiments": "Evaluation plan", "conclusion": "Conclusion"}


def load(path):
    return json.loads(read(path))


def run_path(name):
    path = (ROOT / "runs" / str(name)).resolve()
    if path.parent != (ROOT / "runs").resolve() or not path.is_dir():
        raise ValueError("Choose a saved run from this workspace")
    return path


def available_runs():
    output = []
    for path in sorted((ROOT / "runs").glob("live-*"), reverse=True):
        try:
            study = load(path / "study_summary.json")
            uploaded = (path / "input_manifest.json").exists() and load(path / "input_manifest.json").get("input_origin") == "uploaded"
            if study.get("status") == "COMPLETED" and study.get("test_only") is False and not uploaded:
                output.append(path.name)
        except (OSError, ValueError):
            continue
    return output


def workspace():
    base = ROOT / "inputs/converted"
    package = ResearchPackage.from_dict(load(base / "research_package.json"))
    return package, load(base / "handover_manifest.json")


def open_run(name):
    path = run_path(name)
    summary = load(path / "study_summary.json")
    if summary.get("status") != "COMPLETED" or summary.get("test_only") is not False:
        raise ValueError("This is not a completed real-model run")
    if (path / "input_manifest.json").exists():
        package = ResearchPackage.from_dict(load(path / "package.json"))
        manifest = load(path / "input_manifest.json")
    else:
        package, manifest = workspace()
    if summary["package_hash"] != digest(package):
        raise ValueError("The saved run belongs to a different research package")
    drafts = {name: Draft.from_dict(load(path / (name + ".json")), package)
              for name in ("v0_input", "generic_final", "guided_final")}
    initial = load(path / "v0_diagnostics.json")
    return {"name": name, "path": path, "summary": summary, "drafts": drafts,
            "initial": initial, "configuration": load(path / "configuration.json"),
            "package": package, "manifest": manifest}


def paper(data, version):
    if version not in data["drafts"]:
        raise ValueError("Unknown draft version")
    return render(data["drafts"][version], data["manifest"])


def citation_links(prose, package):
    sources = {s.source_id: s.url for s in package.sources}
    return CITATION.sub(lambda m: "[" + m[1] + "](" + sources[m[1]] + ")", prose)


def score_rows(data):
    initial = data["initial"]
    rows = [{"Version": "Original V0", "Review points flagged by rules": initial["score"],
             "Review points flagged by the LLM": initial.get("qualitative_critic", {}).get("actionable_count")}]
    for arm, label in (("generic", "Generic V1"), ("guided", "Guided V2")):
        diag = data["summary"]["results"][arm]["final_diagnostics"]
        rows.append({"Version": label, "Review points flagged by rules": diag["score"],
                     "Review points flagged by the LLM": diag.get("qualitative_critic", {}).get("actionable_count")})
    return rows


def findings(data):
    return [{"paragraph_id": p["paragraph_id"], "method": "LLM", **f}
            for p in data["initial"].get("qualitative_critic", {}).get("paragraphs", [])
            for f in p["findings"] if f["status"] == "ACTIONABLE"]


def uploaded_project(package_bytes, draft_bytes):
    package, draft, manifest = validate_upload(package_bytes, draft_bytes)
    return {"name": "upload-" + digest(draft)[:16], "package": package, "manifest": manifest,
            "drafts": {"v0_input": draft}, "initial": diagnose(draft), "summary": None}


def comparison_rows(data):
    initial = data["initial"]
    final = data["summary"]["results"]["guided"]["final_diagnostics"] if data["summary"] else None
    return [{"Detection method": "Rule-based checks", "Before refinement": initial["score"],
             "After refinement": final["score"] if final else None},
            {"Detection method": "LLM writing review", "Before refinement": initial.get("qualitative_critic", {}).get("actionable_count"),
             "After refinement": final.get("qualitative_critic", {}).get("actionable_count") if final else None}]


def paragraph_label(data, pid):
    paragraphs = list(data["drafts"]["v0_input"].paragraphs)
    p = next(p for p in paragraphs if p.paragraph_id == pid)
    peers = [block for block in paragraphs if block.section == p.section]
    return SECTIONS[p.section] + " · Paragraph " + str(next(i for i, block in enumerate(peers, 1) if block.paragraph_id == pid))


def point_label(item):
    if item["criterion"] == "specificity" and "vague" in item["explanation"].lower():
        return "Unclear wording"
    return {"specificity": "More detail needed", "argument_strength": "Reasoning needs clarification",
            "formulaic_language": "Formulaic wording", "inappropriate_hedging": "Unnecessary qualifications",
            "generic_transitions": "Generic linking phrase", "unnatural_symmetry": "Repetitive structure"}.get(item["criterion"], "Suggested improvement")


def source_location(evidence):
    parts = [part.strip() for part in evidence.locator.split(";")]
    if parts[0].startswith("Stage A "):
        parts = [part for part in parts[1:] if not part.startswith("https://")]
    return "; ".join(parts) or "See the source for the passage location."


def stop_explanation(reason):
    return {"NO_ACTIONABLE_DIAGNOSTICS": "No further changes were suggested.",
            "UNCHANGED_OR_REPEATED": "The rewrite made no new changes.",
            "INSUFFICIENT_IMPROVEMENT": "The rewrite did not reduce the flagged review points enough.",
            "MAJOR_DRIFT": "The rewrite changed protected content.",
            "CITATION_MISMATCH": "The rewrite changed a citation or its attribution.",
            "UNSUPPORTED_ADDITION": "The rewrite added an unsupported claim.",
            "CHECK_ERROR": "A check could not be completed.",
            "ACCEPTED": "The changes passed the checks and reduced the flagged review points."}.get(reason, reason.replace("_", " ").capitalize() + ".")


def changes(data, version="guided_final"):
    before = {p.paragraph_id: p for p in data["drafts"]["v0_input"].paragraphs}
    return [{"paragraph_id": p.paragraph_id, "section": SECTIONS[p.section],
             "before": before[p.paragraph_id].text, "after": p.text}
            for p in data["drafts"][version].paragraphs if before[p.paragraph_id].text != p.text]


def marked_diff(before, after):
    def escape(s): return re.sub(r"([\\`*_{}\[\]()<>#+!|~])", r"\\\1", s)
    left, right = re.findall(r"\S+|\s+", before), re.findall(r"\S+|\s+", after)
    result = []
    for op, a, b, c, d in SequenceMatcher(None, left, right, autojunk=False).get_opcodes():
        if op == "equal": result.append(escape("".join(left[a:b])))
        if op in {"replace", "delete"}: result.append("~~" + escape("".join(left[a:b])) + "~~")
        if op in {"replace", "insert"}: result.append(":green-background[" + escape("".join(right[c:d])) + "]")
    return "".join(result)


def usage(data):
    calls = [e for e in map(json.loads, read(data["path"] / "events.jsonl").splitlines()) if e["kind"] == "model_call"]
    core = [e for e in calls if not e["stage"].startswith("calibration_")]
    known = [e for e in core if e.get("usage")]
    cost = sum(((Decimal(e["usage"]["input_tokens"]) * RATES[e["model"]][0] +
                 Decimal(e["usage"]["output_tokens"]) * RATES[e["model"]][1]) / Decimal(1_000_000)
                for e in known), Decimal(0))
    return {"core_model_calls": len(core), "development_check_calls": len(calls) - len(core),
            "core_model_seconds": round(sum(e["elapsed_seconds"] for e in core), 1),
            "reported_input_tokens": sum(e["usage"]["input_tokens"] for e in known),
            "reported_output_tokens": sum(e["usage"]["output_tokens"] for e in known),
            "known_core_token_cost_estimate_usd": str(cost), "unknown_usage_calls": len(core) - len(known)}


class NoModel:
    model, test_only = "no-model-in-deliberate-safety-test", True

    def generate(self, *args):
        raise AssertionError("The changed number must fail before a model call")


class InjectedNumber:
    model, test_only = "deliberate-edit-not-an-llm-response", True

    def __init__(self, pid, prose): self.pid, self.prose = pid, prose

    def generate(self, *args):
        return {"edits": [{"paragraph_id": self.pid, "text": self.prose}]}


def number_challenge(data):
    accepted = data["drafts"]["guided_final"]
    p = next(p for p in accepted.paragraphs if "planned pilot contains 20" in p.text)
    injected = p.text.replace("contains 20", "contains 21", 1)
    store = RunStore(ROOT / "verification/ui-safety" / uuid.uuid4().hex)
    store.write("accepted_input.json", accepted)
    store.write("test_configuration.json", {"kind": "DELIBERATE_INJECTED_EDIT_NOT_LLM_OUTPUT",
        "source_run": data["name"], "source_accepted_hash": digest(accepted), "forced_scope": p.paragraph_id,
        "scope_note": "Forced for a controlled safety exercise; not selected by the critic.", "api_calls": 0})
    result = run_arm(data["package"], accepted, InjectedNumber(p.paragraph_id, injected),
        LockedTablesGate(SemanticGate(NoModel()), data["manifest"]), store, "guided", RunConfig(max_attempts=1),
        (p.paragraph_id,), initial_report=diagnose(accepted))
    attempt = result["attempts"][0]
    unchanged = result["final_hash"] == digest(accepted)
    if attempt["reason"] != "MAJOR_DRIFT" or attempt["accepted"] or not unchanged:
        raise ValueError("The controlled safety check did not behave as expected")
    return {"kind": "DELIBERATE_INJECTED_EDIT_NOT_LLM_OUTPUT", "before": p.text, "candidate": injected,
            "paragraph_id": p.paragraph_id, "reason": attempt["preservation"]["reasons"][0],
            "rejected": True, "accepted_draft_retained": unchanged, "api_calls": 0,
            "accepted_hash": digest(accepted), "retained_hash": result["final_hash"],
            "record_id": store.directory.name}
