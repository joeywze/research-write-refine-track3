"""Read and validate Team A's Research Package and the writing draft."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any

VERSION = "0.1"
SECTIONS = ("abstract", "introduction", "related_work", "methodology", "experiments", "conclusion")
CITATION = re.compile(r"\[\[([A-Za-z][A-Za-z0-9_-]*)\]\]")
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")


class CitationError(ValueError):
    """The draft's citation tokens do not match its package claims."""


def digest(value: Any) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def fields(data: dict, expected: set[str], label: str) -> None:
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError(f"{label}: expected exactly {sorted(expected)}")


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: non-empty text required")
    return value


def strings(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{label}: list required")
    result = tuple(text(v, label) for v in value)
    if len(set(result)) != len(result):
        raise ValueError(f"{label}: duplicate entries")
    return result


def identifier(value: Any, label: str) -> str:
    value = text(value, label)
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label}: use letters, digits, underscores or hyphens, starting with a letter")
    return value


def paragraph_text(value: Any) -> str:
    prose = text(value, "paragraph text")
    if re.search(r"\n\s*\n|^\s*#", prose, re.M):
        raise ValueError("Expected one paragraph without section headings")
    return prose


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_id: str
    excerpt: str
    locator: str


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    url: str


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    kind: str
    evidence_ids: tuple[str, ...]
    qualifications: tuple[str, ...]


@dataclass(frozen=True)
class ResearchPackage:
    schema_version: str
    package_id: str
    title: str
    research_question: str
    gap: str
    contribution: str
    methodology: str
    study_status: str
    sources: tuple[Source, ...]
    evidence: tuple[Evidence, ...]
    claims: tuple[Claim, ...]
    technical_terms: tuple[str, ...]
    limitations: tuple[str, ...]
    unknowns: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict) -> ResearchPackage:
        fields(data, set(cls.__dataclass_fields__), "ResearchPackage")
        if data["schema_version"] != VERSION:
            raise ValueError(f"Unsupported package schema; expected {VERSION}")
        if data["study_status"] not in {"proposed", "completed"}:
            raise ValueError("study_status must be proposed or completed")
        for key in ("sources", "evidence", "claims"):
            if not isinstance(data[key], (list, tuple)) or not data[key]:
                raise ValueError(f"{key}: non-empty list required")
        sources, evidence, claims = [], [], []
        for item in data["sources"]:
            fields(item, set(Source.__dataclass_fields__), "Source")
            sources.append(Source(identifier(item["source_id"], "source_id"),
                                  text(item["title"], "source title"), text(item["url"], "source URL")))
        for item in data["evidence"]:
            fields(item, set(Evidence.__dataclass_fields__), "Evidence")
            evidence.append(Evidence(identifier(item["evidence_id"], "evidence_id"),
                                     identifier(item["source_id"], "source_id"),
                                     text(item["excerpt"], "excerpt"), text(item["locator"], "locator")))
        for item in data["claims"]:
            fields(item, set(Claim.__dataclass_fields__), "Claim")
            if item["kind"] not in {"source", "proposal", "result"}:
                raise ValueError("claim kind must be source, proposal or result")
            ids = strings(item["evidence_ids"], "evidence_ids")
            if item["kind"] != "proposal" and not ids:
                raise ValueError("Source and result claims need evidence")
            if item["kind"] == "result" and data["study_status"] != "completed":
                raise ValueError("A proposed study cannot contain its own result claims")
            claims.append(Claim(identifier(item["claim_id"], "claim_id"), text(item["text"], "claim text"),
                                item["kind"], ids, strings(item["qualifications"], "qualifications")))
        for items, key in ((sources, "source_id"), (evidence, "evidence_id"), (claims, "claim_id")):
            if len({getattr(v, key) for v in items}) != len(items):
                raise ValueError(f"Duplicate {key}")
        source_ids = {s.source_id for s in sources}
        evidence_ids = {e.evidence_id for e in evidence}
        if any(e.source_id not in source_ids for e in evidence):
            raise ValueError("Evidence refers to an unknown source")
        if any(not set(c.evidence_ids) <= evidence_ids for c in claims):
            raise ValueError("Claim refers to unknown evidence")
        scalar = {key: text(data[key], key) for key in
                  ("title", "research_question", "gap", "contribution", "methodology")}
        return cls(VERSION, identifier(data["package_id"], "package_id"), **scalar,
                   study_status=data["study_status"], sources=tuple(sources), evidence=tuple(evidence),
                   claims=tuple(claims), technical_terms=strings(data["technical_terms"], "technical_terms"),
                   limitations=strings(data["limitations"], "limitations"),
                   unknowns=strings(data["unknowns"], "unknowns"))


@dataclass(frozen=True)
class Paragraph:
    paragraph_id: str
    section: str
    text: str
    claim_ids: tuple[str, ...]


@dataclass(frozen=True)
class Draft:
    schema_version: str
    package_id: str
    paragraphs: tuple[Paragraph, ...]

    @classmethod
    def from_dict(cls, data: dict, package: ResearchPackage) -> Draft:
        fields(data, set(cls.__dataclass_fields__), "Draft")
        if data["schema_version"] != VERSION or data["package_id"] != package.package_id:
            raise ValueError("Draft schema/package does not match ResearchPackage")
        if not isinstance(data["paragraphs"], (list, tuple)) or not data["paragraphs"]:
            raise ValueError("Draft needs paragraphs")
        paragraphs = []
        known_claims = {c.claim_id: c for c in package.claims}
        evidence_sources = {e.evidence_id: e.source_id for e in package.evidence}
        source_ids = {s.source_id for s in package.sources}
        for item in data["paragraphs"]:
            fields(item, set(Paragraph.__dataclass_fields__), "Paragraph")
            if item["section"] not in SECTIONS:
                raise ValueError("Unknown section")
            ids = strings(item["claim_ids"], "claim_ids")
            if not ids or not set(ids) <= known_claims.keys():
                raise ValueError("Each paragraph needs known claim IDs")
            prose = paragraph_text(item["text"])
            citations = set(CITATION.findall(prose))
            if not citations <= source_ids:
                raise CitationError("Unknown citation token")
            # Cite each supporting source in the paragraph that uses its claim.
            required = {evidence_sources[eid] for cid in ids for eid in known_claims[cid].evidence_ids}
            if not required <= citations:
                raise CitationError("Missing supporting citation for paragraph claim")
            paragraphs.append(Paragraph(identifier(item["paragraph_id"], "paragraph_id"),
                                        item["section"], prose, ids))
        if len({p.paragraph_id for p in paragraphs}) != len(paragraphs):
            raise ValueError("Duplicate paragraph ID")
        if set(p.section for p in paragraphs) != set(SECTIONS):
            raise ValueError("All six sections are required")
        indices = [SECTIONS.index(p.section) for p in paragraphs]
        if indices != sorted(indices):
            raise ValueError("Paragraphs must follow the six-section order")
        if {cid for p in paragraphs for cid in p.claim_ids} != set(known_claims):
            raise ValueError("Draft must cover all package claims")
        return cls(VERSION, package.package_id, tuple(paragraphs))

    def markdown(self, package: ResearchPackage) -> str:
        lines = [f"# {package.title}", ""]
        for section in SECTIONS:
            lines.extend(["## " + section.replace("_", " ").title(), ""])
            for paragraph in self.paragraphs:
                if paragraph.section == section:
                    lines.extend([paragraph.text, ""])
        lines.extend(["## References", ""])
        used = {cid for p in self.paragraphs for cid in CITATION.findall(p.text)}
        for source in package.sources:
            if source.source_id in used:
                lines.append(f"[[{source.source_id}]] {source.title}. {source.url}")
        return "\n".join(lines) + "\n"
