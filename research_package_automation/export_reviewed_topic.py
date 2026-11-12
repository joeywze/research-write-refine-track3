"""Export an existing reviewed topic folder to the shared Stage B schema.

This exporter preserves the reviewed Markdown draft. It does not ask a model to
rewrite the research. Topic-specific scientific choices live in a small reviewed
configuration file, while paragraph positions and citations are derived from the
draft itself.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict
import json
from pathlib import Path
import re

from research_package_automation.support.contracts import Draft, ResearchPackage
from research_package_automation.research_package_builder import MASTER_COLUMNS


ACL_LINK = re.compile(
    r"\[([^\]\n]+)\]\((https://aclanthology\.org/((?:19|20)\d{2}\.[a-z][a-z0-9-]*\.\d+)[^)]*)\)"
)
EVIDENCE_HEADING = re.compile(r"(?m)^## ([CE]\d+): (.+)$")
SECTION_NAMES = {
    "abstract": "abstract",
    "1. introduction": "introduction",
    "2. related work and gap establishment": "related_work",
    "3. methodology": "methodology",
    "4. experiments and evaluation plan": "experiments",
    "5. conclusion": "conclusion",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def source_id(paper_id: str) -> str:
    return "S_" + re.sub(r"[^A-Za-z0-9]+", "_", paper_id).strip("_")


def evidence_id(paper_id: str, number: int) -> str:
    return "E_" + re.sub(r"[^A-Za-z0-9]+", "_", paper_id).strip("_") + f"_{number:02d}"


def parse_evidence_file(path: Path) -> dict[str, dict]:
    """Read the reviewed short passages without changing their wording."""
    text = read(path)
    matches = list(EVIDENCE_HEADING.finditer(text))
    records = {}
    for index, match in enumerate(matches):
        block = text[match.start(): matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        paper = re.search(
            r"Paper ID: \[([^\]]+)\]\((https://aclanthology\.org/[^)]+)\)\.?", block
        )
        if not paper:
            continue
        paper_id, canonical_url = paper.groups()
        rows = []
        for line in block.splitlines():
            if not line.startswith("|") or "Exact short passage" in line or re.fullmatch(r"\|[-| ]+\|", line):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != 3:
                continue
            location = re.search(r"\[([^\]]+)\]\((https://aclanthology\.org/[^)]+)\)", cells[2])
            if not location:
                continue
            excerpt = cells[1].strip().strip("\"“”")
            if excerpt:
                rows.append({"topic": cells[0], "excerpt": excerpt,
                             "locator": location[1], "url": location[2]})
        if not rows:
            continue
        records[paper_id] = {
            "title": match[2].strip(), "url": canonical_url, "rows": rows,
        }
    return records


def parse_evidence(topic_dir: Path) -> dict[str, dict]:
    combined = {}
    for name in ("claim_evidence_table.md", "external_evidence.md"):
        path = topic_dir / name
        if path.exists():
            overlap = set(combined) & set(parse_evidence_file(path))
            if overlap:
                raise ValueError(f"Duplicate evidence records across files: {sorted(overlap)}")
            combined.update(parse_evidence_file(path))
    return combined


def parse_draft(path: Path) -> tuple[str, list[dict]]:
    text = read(path)
    title_match = re.search(r"(?m)^# (.+)$", text)
    if not title_match:
        raise ValueError("Draft needs a level-one title")
    section = None
    blocks: list[dict] = []
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        prose = "\n".join(buffer).strip()
        if prose and section:
            blocks.append({"section": section, "raw": prose})
        buffer = []

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            heading = line[3:].strip().lower()
            if heading == "references":
                section = None
                break
            section = SECTION_NAMES.get(heading)
            if not section:
                raise ValueError(f"Unsupported top-level draft section: {line[3:].strip()}")
            continue
        if line.startswith("### "):
            flush()
            continue
        if not section:
            continue
        if not line.strip():
            flush()
        else:
            buffer.append(line)
    flush()
    if {block["section"] for block in blocks} != set(SECTION_NAMES.values()):
        raise ValueError("Draft must contain all six shared sections")
    return title_match[1].strip(), blocks


def citation_context(raw: str, paper_id: str) -> str:
    """Return visible draft context for a provisional, review-required mapping."""
    plain = ACL_LINK.sub(lambda match: match[1], raw).replace("\n", " ")
    matching_labels = [match[1] for match in ACL_LINK.finditer(raw) if match[3] == paper_id]
    label = "; ".join(matching_labels)
    return f"Draft citation context: {label}. Paragraph context: {plain}"


def export_topic(topic_dir: Path, output_dir: Path) -> dict:
    config = json.loads(read(topic_dir / "handover_config.json"))
    expected = {"package_id", "research_question", "gap", "contribution", "technical_terms",
                "limitations", "unknowns"}
    if set(config) != expected:
        raise ValueError(f"handover_config.json must contain exactly {sorted(expected)}")
    title, raw_blocks = parse_draft(topic_dir / "draft_v0.md")
    reviewed = parse_evidence(topic_dir)
    used_papers = []
    for block in raw_blocks:
        for match in ACL_LINK.finditer(block["raw"]):
            if match[3] not in used_papers:
                used_papers.append(match[3])
    missing = [paper_id for paper_id in used_papers if paper_id not in reviewed]
    if missing:
        raise ValueError(f"Draft citations lack reviewed evidence records: {missing}")

    sources, evidence = [], []
    evidence_by_paper = defaultdict(list)
    for paper_id in used_papers:
        record = reviewed[paper_id]
        sources.append({"source_id": source_id(paper_id), "title": record["title"], "url": record["url"]})
        for number, row in enumerate(record["rows"], 1):
            eid = evidence_id(paper_id, number)
            evidence_by_paper[paper_id].append(eid)
            evidence.append({"evidence_id": eid, "source_id": source_id(paper_id),
                             "excerpt": row["excerpt"], "locator": row["locator"]})

    paragraphs, claims, fact_rows = [], [], []
    for number, block in enumerate(raw_blocks, 1):
        pid = f"P{number:03d}"
        cited_papers = []
        for match in ACL_LINK.finditer(block["raw"]):
            if match[3] not in cited_papers:
                cited_papers.append(match[3])
        converted = ACL_LINK.sub(lambda match: "[[" + source_id(match[3]) + "]]", block["raw"])
        proposal_id = "C_" + pid + "_AUTHOR"
        claim_ids = [proposal_id]
        claims.append({
            "claim_id": proposal_id,
            "text": "Author framing or proposed-study content retained from " + pid + ".",
            "kind": "proposal", "evidence_ids": [],
            "qualifications": ["Retained from the reviewed Draft V0; not an observed result."],
        })
        for source_number, paper_id in enumerate(cited_papers, 1):
            claim_id = f"C_{pid}_SOURCE_{source_number:02d}"
            claim_ids.append(claim_id)
            claims.append({
                "claim_id": claim_id,
                "text": citation_context(block["raw"], paper_id),
                "kind": "source", "evidence_ids": evidence_by_paper[paper_id],
                "qualifications": [
                    "Provisional citation-context mapping generated from reviewed materials.",
                    "Half 1 must approve the attributed claim before production use.",
                    "A verified excerpt does not independently reproduce the cited study.",
                ],
            })
            source_record = reviewed[paper_id]
            evidence_lookup = {row["evidence_id"]: row for row in evidence}
            for eid in evidence_by_paper[paper_id]:
                entry = evidence_lookup[eid]
                fact_rows.append(dict(zip(MASTER_COLUMNS, (
                    claim_id, source_id(paper_id), source_record["title"],
                    citation_context(block["raw"], paper_id), entry["excerpt"], entry["locator"],
                    "UNREVIEWED", source_record["url"], "reviewed_topic_export", "",
                    "Citation-context mapping requires Half 1 approval.",
                ))))
        paragraphs.append({"paragraph_id": pid, "section": block["section"],
                           "text": converted, "claim_ids": claim_ids})

    methodology = "\n\n".join(
        ACL_LINK.sub(lambda match: "[[" + source_id(match[3]) + "]]", block["raw"])
        for block in raw_blocks if block["section"] == "methodology"
    )
    package_data = {
        "schema_version": "0.1", "package_id": config["package_id"], "title": title,
        "research_question": config["research_question"], "gap": config["gap"],
        "contribution": config["contribution"], "methodology": methodology,
        "study_status": "proposed", "sources": sources, "evidence": evidence, "claims": claims,
        "technical_terms": config["technical_terms"], "limitations": config["limitations"],
        "unknowns": config["unknowns"],
    }
    draft_data = {"schema_version": "0.1", "package_id": config["package_id"],
                  "paragraphs": paragraphs}
    package = ResearchPackage.from_dict(package_data)
    draft = Draft.from_dict(draft_data, package)
    prose = "\n".join(paragraph["text"] for paragraph in paragraphs)
    absent_terms = [term for term in config["technical_terms"] if term.lower() not in prose.lower()]
    if absent_terms:
        raise ValueError(f"Protected terms are absent from Draft V0: {absent_terms}")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "research_package.json").write_text(
        json.dumps(asdict(package), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "v0.json").write_text(
        json.dumps(asdict(draft), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    from openpyxl import Workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Master"
    sheet.append(MASTER_COLUMNS)
    for row in fact_rows:
        sheet.append([row[column] for column in MASTER_COLUMNS])
    for cells in sheet:
        for cell in cells:
            if isinstance(cell.value, str):
                cell.data_type = "s"
    workbook.save(output_dir / "master_facts.xlsx")
    manifest = {
        "status": "PROVISIONAL_AUTOMATED_MAPPING",
        "topic_directory": str(topic_dir),
        "paragraphs": len(paragraphs), "sources": len(sources), "evidence_records": len(evidence),
        "fact_check_records": len(fact_rows),
        "production_ready": False,
        "fact_check_status": "NOT_RUN",
        "review_boundary": "Automated citation-context mappings are unapproved and intended for demonstration use.",
    }
    (output_dir / "export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(export_topic(args.topic_dir, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
