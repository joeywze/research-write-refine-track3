"""Check fixed content and meaning before accepting a draft."""

from collections import Counter
from dataclasses import asdict, dataclass
import re

from .contracts import CITATION, CitationError, Draft, ResearchPackage, digest, fields, strings
from .prompts import CHECK_INSTRUCTIONS, CHECK_SCHEMA, STATUSES
from .providers import BudgetExceeded

NUMBERS = re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)*(?:%|\b)")
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$|\\\(.*?\\\)|\\\[.*?\\\]", re.S)


@dataclass(frozen=True)
class PreservationResult:
    status: str
    reasons: tuple[str, ...]
    semantic: dict | None = None


def tokens(pattern, prose):
    return Counter(pattern.findall(CITATION.sub("", prose)))


def term_count(term, prose):
    return len(re.findall(r"(?<!\w)" + re.escape(term) + r"(?!\w)", prose, re.I))


def deterministic(package: ResearchPackage, candidate: Draft, references: tuple[Draft, ...]) -> PreservationResult:
    try:
        Draft.from_dict(asdict(candidate), package)
    except CitationError as error:
        return PreservationResult("CITATION_MISMATCH", (str(error),))
    except (ValueError, TypeError, KeyError) as error:
        return PreservationResult("MAJOR_DRIFT", (str(error),))
    if not references:
        supported = " ".join([package.research_question, package.gap, package.contribution,
                              package.methodology, *package.limitations, *package.unknowns,
                              *(e.excerpt for e in package.evidence), *(c.text for c in package.claims),
                              *(q for c in package.claims for q in c.qualifications)])
        allowed = set(NUMBERS.findall(supported))
        for p in candidate.paragraphs:
            if set(tokens(NUMBERS, p.text)) - allowed:
                return PreservationResult("UNSUPPORTED_ADDITION", (f"{p.paragraph_id}: number absent from package evidence/claims",))
        prose = "\n".join(p.text for p in candidate.paragraphs)
        missing = [t for t in package.technical_terms if not term_count(t, prose)]
        if missing:
            return PreservationResult("MAJOR_DRIFT", (f"V0 omits protected terms: {missing}",))
    for reference in references:
        if candidate.package_id != reference.package_id or len(candidate.paragraphs) != len(reference.paragraphs):
            return PreservationResult("MAJOR_DRIFT", ("Paragraph structure changed",))
        for before, after in zip(reference.paragraphs, candidate.paragraphs):
            if (before.paragraph_id, before.section, before.claim_ids) != (after.paragraph_id, after.section, after.claim_ids):
                return PreservationResult("MAJOR_DRIFT", ("Paragraph identity, order, section or claim mapping changed",))
            if Counter(CITATION.findall(before.text)) != Counter(CITATION.findall(after.text)):
                return PreservationResult("CITATION_MISMATCH", (f"{before.paragraph_id}: citations changed",))
            if tokens(NUMBERS, before.text) != tokens(NUMBERS, after.text):
                return PreservationResult("MAJOR_DRIFT", (f"{before.paragraph_id}: numbers changed",))
            if tokens(MATH, before.text) != tokens(MATH, after.text):
                return PreservationResult("MAJOR_DRIFT", (f"{before.paragraph_id}: mathematical expressions changed",))
            for term in package.technical_terms:
                if term_count(term, before.text) != term_count(term, after.text):
                    return PreservationResult("MAJOR_DRIFT", (f"{before.paragraph_id}: protected term changed: {term}",))
    return PreservationResult("PASS", ())


class SemanticGate:
    def __init__(self, provider, max_output_tokens: int = 4000):
        self.provider = provider
        self.model = provider.model
        self.test_only = provider.test_only
        self.max_output_tokens = max_output_tokens

    def check(self, package: ResearchPackage, candidate: Draft, references=()) -> PreservationResult:
        basic = deterministic(package, candidate, tuple(references))
        if basic.status != "PASS":
            return basic
        try:
            payload = {"package": asdict(package), "candidate": asdict(candidate),
                       "references": [asdict(r) for r in references],
                       "package_hash": digest(package), "candidate_hash": digest(candidate)}
            result = self.provider.generate("preservation", CHECK_INSTRUCTIONS, payload,
                                            CHECK_SCHEMA, self.max_output_tokens)
            fields(result, {"global_status", "global_reasons", "paragraphs"}, "semantic audit")
            global_reasons = strings(result["global_reasons"], "global_reasons")
            if result["global_status"] not in STATUSES or not isinstance(result["paragraphs"], list):
                raise ValueError("Invalid semantic status or paragraph list")
            expected = {p.paragraph_id: set(p.claim_ids) for p in candidate.paragraphs}
            seen, failures = set(), []
            for item in result["paragraphs"]:
                fields(item, {"paragraph_id", "status", "checked_claim_ids", "reasons"}, "paragraph audit")
                pid = item["paragraph_id"]
                if pid not in expected or pid in seen or item["status"] not in STATUSES:
                    raise ValueError("Unknown/duplicate paragraph or invalid verdict")
                seen.add(pid)
                if set(strings(item["checked_claim_ids"], "checked_claim_ids")) != expected[pid]:
                    raise ValueError("Incomplete claim audit")
                reasons = strings(item["reasons"], "reasons")
                if item["status"] != "PASS":
                    if not reasons:
                        raise ValueError("Failure needs a reason")
                    failures.append((item["status"], tuple(f"{pid}: {r}" for r in reasons)))
            if seen != set(expected):
                raise ValueError("Semantic audit omitted paragraphs")
            if result["global_status"] != "PASS":
                if not global_reasons:
                    raise ValueError("Global failure needs a reason")
                failures.insert(0, (result["global_status"], global_reasons))
            if failures:
                return PreservationResult(failures[0][0], tuple(r for _, rs in failures for r in rs), result)
            return PreservationResult("PASS", (), result)
        except BudgetExceeded:
            raise
        except Exception as error:
            return PreservationResult("CHECK_ERROR", (f"Semantic check failed: {type(error).__name__}: {error}",))
