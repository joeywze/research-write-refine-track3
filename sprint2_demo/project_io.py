"""Validate a paired research package and draft without changing the example."""
from dataclasses import asdict
import json
from pathlib import Path
from urllib.parse import urlparse

from handover import Draft, ResearchPackage, CITATION, render
from src.writing.contracts import SECTIONS, digest

MAX_FILE_BYTES = 1_000_000
MAX_BLOCKS = 60
MAX_WORDS = 12_000


def decode(data):
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_FILE_BYTES:
        raise ValueError("Each JSON file must be non-empty and no larger than 1 MB.")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("JSON contains a repeated field: " + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("JSON contains an invalid number.")

    try:
        return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique, parse_constant=invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("Use a valid UTF-8 JSON file.") from error


def basic_manifest(package, draft):
    """Keep every paragraph, table and citation in a contract-only upload."""
    sources = {s.source_id: s for s in package.sources}
    layout, blocks = ["# " + package.title + "\n\n"], []
    for section in SECTIONS:
        label = "Experiments: Evaluation plan" if section == "experiments" and package.study_status == "proposed" else section.replace("_", " ").capitalize()
        layout.append("## " + label + "\n\n")
        for p in draft.paragraphs:
            if p.section != section:
                continue
            occurrences = [{"source_id": sid, "original_markdown": "[" + sid + "](" + sources[sid].url + ")"}
                           for sid in CITATION.findall(p.text)]
            blocks.append({"paragraph_id": p.paragraph_id, "section": p.section,
                "kind": "table" if p.text.lstrip().startswith("|") else "prose",
                "locked": p.text.lstrip().startswith("|"), "converted_text": p.text,
                "citation_occurrences": occurrences})
            layout.extend([{"paragraph_id": p.paragraph_id}, "\n\n"])
    layout.append("## References\n\n")
    layout.append("\n".join("- [" + s.source_id + "](" + s.url + ") " + s.title for s in package.sources) + "\n")
    return {"input_origin": "uploaded", "package_hash": digest(package), "draft_hash": digest(draft),
        "layout": layout, "blocks": blocks, "source_support_warnings": [],
        "source_approval": "NOT_VERIFIED", "evidence_provenance": [
            {"evidence_id": e.evidence_id, "paper_id": e.source_id,
             "source_kind": "reviewer_context_uploaded" if e.excerpt.startswith("Stage A reviewer context/interpretation") else "uploaded_not_independently_verified"} for e in package.evidence]}


def validate_upload(package_bytes, draft_bytes):
    package = ResearchPackage.from_dict(decode(package_bytes))
    draft = Draft.from_dict(decode(draft_bytes), package)
    for source in package.sources:
        url = urlparse(source.url)
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("Source links must be HTTPS links without credentials.")
    if len(draft.paragraphs) > MAX_BLOCKS or sum(len(p.text.split()) for p in draft.paragraphs) > MAX_WORDS:
        raise ValueError("This demo accepts up to 60 content blocks and 12,000 draft words.")
    manifest = basic_manifest(package, draft)
    # Exercise the export before accepting an upload.
    render(draft, manifest)
    return package, draft, manifest


def save_input(directory, package, draft, manifest):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for name, value in (("research_package.json", asdict(package)), ("v0.json", asdict(draft)),
                        ("handover_manifest.json", manifest)):
        (directory / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_input(directory):
    directory = Path(directory)
    package, draft, generated = validate_upload((directory / "research_package.json").read_bytes(),
                                                (directory / "v0.json").read_bytes())
    manifest = json.loads((directory / "handover_manifest.json").read_text(encoding="utf-8-sig"))
    if manifest.get("input_origin") == "uploaded":
        if manifest != generated:
            raise ValueError("The uploaded project no longer matches its checked inputs.")
    elif directory.resolve() != (Path(__file__).parent / "inputs/converted").resolve():
        raise ValueError("Only the pinned example can supply its own layout manifest.")
    return package, draft, manifest
