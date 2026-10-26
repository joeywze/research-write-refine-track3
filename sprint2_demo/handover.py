"""Adapt the pinned provisional paper without editing the research source files."""

from collections import Counter, defaultdict, deque
from dataclasses import asdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))
from src.writing.contracts import Draft, ResearchPackage, CITATION
from src.writing.preservation import PreservationResult

LINK = re.compile(r"\[([^\]\n]+)\]\((https://aclanthology\.org/[^)\s]+)\)")
PAPER_ID = re.compile(r"https://aclanthology\.org/((?:19|20)\d{2}\.[a-z][a-z0-9-]*\.\d+)")
SECTION = {
    "Abstract": "abstract", "1. Introduction": "introduction",
    "2. Related Work": "related_work", "3. Methodology": "methodology",
    "4. Experiments: Evaluation Plan": "experiments", "5. Conclusion": "conclusion",
}
STAGE_A = "01915001d9490914eb2f1a316c1ea06053adfaef"
STAGE_B = "f108a13eb6625fccc80bc5d57d435797519a1255"


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evidence_records(path):
    """Keep short excerpts distinct from Stage A's contextual interpretation."""
    records = defaultdict(list)
    for block in re.split(r"(?m)(?=^## )", read(path)):
        paper = PAPER_ID.search(block)
        if not paper:
            continue
        paper_id = paper[1]
        heading = block.splitlines()[0]
        for line in block.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 3:
                continue
            location = LINK.search(cells[2])
            if not location:
                continue
            excerpt = cells[1].strip('"“”')
            records[paper_id].append({
                "excerpt": excerpt,
                "locator": f"Stage A {path.name}, {heading}; {location[1]}; {location[2]}",
                "source_kind": "passage_transcribed_in_stage_a_review",
            })
        context = re.search(r"(?m)^Context: (.+)$", block)
        if context:
            records[paper_id].append({
                "excerpt": "Stage A reviewer context/interpretation, not a verbatim primary-source passage: " + context[1],
                "locator": f"Stage A {path.name}, {heading}, Context paragraph",
                "source_kind": "reviewer_context_not_independently_reverified",
            })
    return records


def source_fact(block_index, paper_id):
    """Explicit claim mapping for the four citation-bearing source blocks."""
    mapping = {
        (5, "2025.findings-emnlp.587"): "Fu and Liu (2025) evaluate judgments on parallel language versions.",
        (5, "2026.mme-main.8"): "Chung and Freienthal (2026) investigate cross-language stability in controlled customer-support dialogues.",
        (12, "2025.emnlp-main.103"): "Wang et al. (2025) explicitly limit their evaluation to English and identify multilingual judging as future work.",
        (12, "2025.emnlp-main.1307"): "Wu et al. (2025) examine translation evaluation across six target languages.",
        (13, "2025.emnlp-main.712"): "Yu et al. (2025) compare an official English prompt with basic and instructional Chinese prompts, which vary in detail as well as language.",
        (13, "2026.mme-main.8"): "Chung and Freienthal (2026) include an Estonian instruction-language sensitivity check.",
        (16, "2025.findings-emnlp.587"): "Fu and Liu (2025) use ground-truth answers as evaluation candidates in parallel multilingual tests.",
        (16, "2026.mme-main.8"): "Chung and Freienthal (2026) conduct controlled dialogue evaluation, with human calibration restricted to Estonian.",
        (16, "2026.acl-srw.33"): "Datta and Baitalik (2026) include correct and incorrect variants in multilingual factual QA; completed human validation remains a limitation of the final rerun.",
        (16, "2025.acl-long.3"): "Gureja et al. (2025) include sampled native-speaker validation in multilingual preference evaluation.",
    }
    try:
        return mapping[(block_index, paper_id)]
    except KeyError:
        raise ValueError(f"No reviewed claim mapping for source block {block_index}, {paper_id}")


def author_framing(block_index, text):
    if block_index == 5:
        return ("When a language model is used to evaluate answers, the evaluator itself becomes an object of assessment. "
                "Their work provides direct precedents for studying language-dependent evaluation, rather than a basis for claiming that multilingual judging has been overlooked.")
    if block_index == 12:
        return ("An English-focused study can motivate extending that study without establishing an absence elsewhere. "
                "The relevant comparison is therefore between specific tasks and evaluation protocols, rather than English-only and multilingual research as mutually exclusive categories.")
    if block_index == 13:
        return ("Judging-instruction language also needs to be distinguished from the language of the evaluated content. "
                "Our secondary condition follows this existing line of inquiry but aims to preserve rubric meaning while changing instruction language.")
    if block_index == 16:
        rows = [line for line in text.splitlines()[2:] if line.strip().startswith("|")]
        return "Author's proposed comparisons: " + " ".join(line.strip("|").split("|")[-1].strip() for line in rows)
    return text


def build():
    source = ROOT / "inputs/source"
    original = read(source / "draft_v0.md")
    pinned = json.loads(read(ROOT / "inputs/source_manifest.json"))
    expected = {Path(item["path"]).name: item["sha"] for item in pinned["files"]}
    for file in source.iterdir():
        data = file.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual != expected[file.name]:
            raise ValueError(f"Pinned source changed: {file.name}; review before rebuilding")
    ledger = json.loads(read(source / "claim_evidence_ledger.json"))
    titles = {claim["paper_id"]: claim["title"] for claim in ledger["claims"]}
    external = read(source / "external_evidence.md")
    for match in LINK.finditer(external):
        paper = PAPER_ID.search(match[2])
        if paper and match[2].endswith("/"):
            titles.setdefault(paper[1], match[1])
    excerpts = evidence_records(source / "claim_evidence_table.md")
    for paper_id, values in evidence_records(source / "external_evidence.md").items():
        excerpts[paper_id].extend(values)

    pieces = re.split(r"(\n[ \t]*\n)", original)
    content_blocks = [pieces[index] for index in range(0, len(pieces), 2)]
    if len(content_blocks) not in {60, 61} or not content_blocks[5].startswith("When a language model"):
        raise ValueError("V0 structure changed; review the explicit claim mapping before rebuilding")
    urls = []
    for block in content_blocks[:58]:
        for match in LINK.finditer(block):
            if match[2] not in urls:
                urls.append(match[2])
    source_id = {url: f"S{index:02d}" for index, url in enumerate(urls, 1)}
    sources = [{"source_id": source_id[url], "title": titles[PAPER_ID.search(url)[1]], "url": url} for url in urls]
    evidence, provenance = [], []
    evidence_by_url = {}
    for url in urls:
        pid = PAPER_ID.search(url)[1]
        if not excerpts[pid]:
            raise ValueError(f"No supplied evidence excerpts for {pid}")
        ids = []
        for index, record in enumerate(excerpts[pid], 1):
            eid = f"E_{source_id[url]}_{index:02d}"
            ids.append(eid)
            evidence.append({"evidence_id": eid, "source_id": source_id[url],
                             "excerpt": record["excerpt"], "locator": record["locator"]})
            provenance.append({"evidence_id": eid, "paper_id": pid, "citation_url": url,
                               "source_kind": record["source_kind"], "excerpt_sha256": sha(record["excerpt"]),
                               "independently_reverified_in_this_integration": False})
        evidence_by_url[url] = ids

    paragraphs, claims, blocks = [], [], []
    section, subsection = None, None
    layout = list(pieces)
    for block_index, raw in enumerate(content_blocks):
        if raw.startswith("## "):
            name = raw[3:].strip()
            section = SECTION.get(name)
            subsection = None
            continue
        if raw.startswith("### "):
            subsection = raw[4:].strip()
            continue
        if not raw.strip() or raw.startswith("# ") or section is None:
            continue
        pid = f"P{len(paragraphs)+1:03d}"
        links = [{"source_id": source_id[m[2]], "original_markdown": m[0]} for m in LINK.finditer(raw)]
        converted = LINK.sub(lambda m: "[[" + source_id[m[2]] + "]]", raw)
        cid = "C_" + pid
        framing = author_framing(block_index, converted)
        claims.append({"claim_id": cid, "text": framing, "kind": "proposal", "evidence_ids": [],
                       "qualifications": ["Author's proposed protocol, framing or interpretation; not an observed result.",
                                          "Team A approval remains pending."]})
        ids = [cid]
        grouped_urls = defaultdict(list)
        for m in LINK.finditer(raw):
            grouped_urls[PAPER_ID.search(m[2])[1]].append(m[2])
        for number, (paper_id, linked_urls) in enumerate(grouped_urls.items(), 1):
            source_claim = cid + f"_S{number}"
            ids.append(source_claim)
            eids = list(dict.fromkeys(eid for url in linked_urls for eid in evidence_by_url[url]))
            claims.append({"claim_id": source_claim, "text": source_fact(block_index, paper_id),
                           "kind": "source", "evidence_ids": eids,
                           "qualifications": ["Evidence carried from the Stage A review; not independently reproduced or reverified here.",
                                              "Some pilot claims are only partially/provisionally supported or have insufficient selected evidence; consult the handover manifest.",
                                              "No field-wide novelty or absence claim follows from an individual paper's limitation."]})
        paragraphs.append({"paragraph_id": pid, "section": section, "text": converted, "claim_ids": ids})
        kind = "table" if raw.startswith("|") else "list" if re.match(r"\d+\. ", raw) else "prose"
        blocks.append({"paragraph_id": pid, "source_block_index": block_index, "piece_index": 2*block_index,
                       "section": section, "subsection": subsection, "kind": kind, "locked": kind == "table",
                       "original_sha256": sha(raw), "converted_sha256": sha(converted),
                       "original_text": raw, "converted_text": converted, "citation_occurrences": links})
        layout[2*block_index] = {"paragraph_id": pid}

    package = {
        "schema_version": "0.1", "package_id": "bilingual_qa_provisional_20261021",
        "title": content_blocks[0][2:], "research_question": content_blocks[8],
        "gap": content_blocks[17] + " The novelty of the combined protocol remains unconfirmed.",
        "contribution": content_blocks[9],
        "methodology": "\n\n".join(p["text"] for p in paragraphs if p["section"] == "methodology"),
        "study_status": "proposed", "sources": sources, "evidence": evidence, "claims": claims,
        "technical_terms": ["Cohen's kappa", "unconditional operational agreement"],
        "limitations": [content_blocks[54], content_blocks[55],
                        "Provisional integration input: Team A approval and complete source support review remain pending."],
        "unknowns": ["Language pair, item source/licence, judge version, raters and budget are not finalised.",
                     "No experiments have been conducted and no performance result is established.",
                     "Novelty of the combined study design remains unconfirmed.",
                     "Some saved pilot source claims have incomplete evidential support."]}
    draft = {"schema_version": "0.1", "package_id": package["package_id"], "paragraphs": paragraphs}
    parsed_package = ResearchPackage.from_dict(package)
    Draft.from_dict(draft, parsed_package)
    pilot = list(csv.DictReader(read(source / "draft_v0_pilot_verification.csv").splitlines()))
    manifest = {"status": "PROVISIONAL_NOT_TEAM_A_APPROVED", "stage_a_revision": STAGE_A,
                "stage_b_revision": STAGE_B, "source_file_sha256": sha(original), "layout": layout, "blocks": blocks,
                "evidence_provenance": provenance, "source_pilot_labels": pilot,
                "source_support_warnings": [p for p in pilot if p["verification_status"] != "SUPPORTED"],
                "note": "Format conversion and traceability are tested separately from semantic grounding and source correctness.",
                "table_policy": "All four tables are retained verbatim and locked during refinement.",
                "protected_term_selection": "Provisional adapter choices: the exact named agreement metrics; not Team A sign-off."}
    output = ROOT / "inputs/converted"
    write_json(output / "research_package.json", package)
    write_json(output / "v0.json", draft)
    write_json(output / "handover_manifest.json", manifest)
    (output / "v0_roundtrip.md").write_text(render(draft, manifest), encoding="utf-8")
    summary = {"paragraph_blocks": len(paragraphs), "table_blocks": sum(b["kind"] == "table" for b in blocks),
               "source_records": len(sources), "unique_papers": len({PAPER_ID.search(s["url"])[1] for s in sources}),
               "claims": len(claims), "evidence_records": len(evidence), "source_support_warnings": len(manifest["source_support_warnings"]),
               "roundtrip_exact": render(draft, manifest) == original, "semantic_grounding": "NOT_CHECKED",
               "team_a_approval": "PENDING"}
    write_json(output / "conversion_summary.json", summary)
    return summary


def render(draft, manifest):
    """Restore unchanged headings, references, spacing and original citation links."""
    data = asdict(draft) if hasattr(draft, "__dataclass_fields__") else draft
    by_id = {p["paragraph_id"]: p["text"] for p in data["paragraphs"]}
    blocks = {b["paragraph_id"]: b for b in manifest["blocks"]}
    result = []
    for segment in manifest["layout"]:
        if isinstance(segment, str):
            result.append(segment)
            continue
        pid = segment["paragraph_id"]
        text = by_id[pid]
        expected = Counter(c["source_id"] for c in blocks[pid]["citation_occurrences"])
        if Counter(CITATION.findall(text)) != expected:
            raise ValueError(f"Cannot restore changed citations in {pid}")
        queues = defaultdict(deque)
        for occurrence in blocks[pid]["citation_occurrences"]:
            queues[occurrence["source_id"]].append(occurrence["original_markdown"])
        result.append(CITATION.sub(lambda m: queues[m[1]].popleft(), text))
    return "".join(result)


class LockedTablesGate:
    """Keep supplied table structure and contents fixed; delegate all other checks."""
    def __init__(self, gate, manifest):
        self.gate = gate
        self.model = gate.model
        self.test_only = gate.test_only
        self.locked = {b["paragraph_id"]: b["converted_text"] for b in manifest["blocks"] if b["locked"]}

    def check(self, package, candidate, references=()):
        for p in candidate.paragraphs:
            if p.paragraph_id in self.locked and p.text != self.locked[p.paragraph_id]:
                return PreservationResult("MAJOR_DRIFT", (f"{p.paragraph_id}: locked table changed",))
        return self.gate.check(package, candidate, references)


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
