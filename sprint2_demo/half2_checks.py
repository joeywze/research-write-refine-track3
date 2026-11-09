"""Every check a rewritten paragraph must pass before Half 2 accepts it.

This module joins the two halves of the team's Half 2 work:

  * Wan Yun's checks (from src/detection/rewrite_loop.py): length, citations,
    numbers and the fluency guard that stops the rewriter "beating" the detector
    by chopping sentences into fragments.
  * Guan Hong's checks (backend/src/writing/preservation.py): the deterministic
    preservation rules against V0 and the last accepted draft, and the LLM
    meaning check (SemanticGate).
  * New for Sprint 3: a "no new facts" rule and an LLM evidence check that
    compares changed sentences with the team's evidence table, so rewrites are
    checked against the sources and not only against V0.

Checks run cheapest first and stop at the first failure, so a rewrite that
breaks a simple rule never costs a model call.
"""

from collections import Counter
from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
import sys

import pandas as pd

from handover import Draft  # noqa: F401  (also puts the pinned backend on sys.path)
from src.writing.contracts import CITATION
from src.writing.preservation import NUMBERS, PreservationResult, deterministic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "detection"))
import rewrite_loop as rl  # noqa: E402  (fluency guard, prompts, detector feedback)

FACTS_FILE = ROOT / "data" / "facts" / "master_facts.xlsx"
ACL_ID = re.compile(r"aclanthology\.org/([^/#\s]+?)(?:\.pdf)?(?:[/#]|$)")

# Wording that reports a finding. A proposal paragraph (a study not yet run)
# must not gain these, or the rewrite has invented a result.
RESULT_WORDS = re.compile(
    r"\b(improv(?:e|es|ed|ement)|outperform\w*|achiev(?:e|es|ed)|significant(?:ly)?|"
    r"we (?:found|find|observed?|show(?:ed)?)|results? (?:show|showed|indicate|indicated|demonstrate|demonstrated)|"
    r"demonstrat(?:e|es|ed)|confirm(?:s|ed)?|reveal(?:s|ed)?)\b", re.I)
# Words that turn a cautious claim into a certain one.
CERTAINTY_WORDS = re.compile(
    r"\b(prove[sd]?|proven|clearly|certainly|definitely|undoubtedly|always|never|guarantee[sd]?|"
    r"conclusively|establish(?:es|ed)?)\b", re.I)
NEGATION = re.compile(r"\b(not|cannot|can't|doesn't|does not|won't|no)\s+(\w+\s+)?$", re.I)


def certainty_words(text):
    """Certainty words that are not negated ("cannot establish" is cautious, not certain)."""
    return Counter(m.group(1).lower() for m in CERTAINTY_WORDS.finditer(text)
                   if not NEGATION.search(text[max(0, m.start() - 25):m.start()]))


@dataclass(frozen=True)
class CheckResult:
    check: str           # which check produced the verdict
    status: str          # PASS or a failure status
    reason: str = ""

    @property
    def passed(self):
        return self.status == "PASS"


def with_paragraph(draft, paragraph_id, text):
    """A copy of the draft with one paragraph's text replaced."""
    return replace(draft, paragraphs=tuple(replace(p, text=text) if p.paragraph_id == paragraph_id else p
                                           for p in draft.paragraphs))


def paragraph(draft, paragraph_id):
    return next(p for p in draft.paragraphs if p.paragraph_id == paragraph_id)


def plain(text):
    """Paragraph text without [[S01]] citation tokens, for scoring and sentence checks."""
    return re.sub(r"\s+([.,;:])", r"\1", CITATION.sub("", text)).strip()


# ---------------------------------------------------------------- cheap checks
def fluency_check(before, after):
    ok, why = rl.content_ok(before, after)          # length within +/-35%, same citations, same numbers
    if not ok:
        return CheckResult("length and tokens", "MAJOR_DRIFT", why)
    ok, why = rl.fluency_ok(plain(after))           # no fragments, few very short sentences
    if not ok:
        return CheckResult("fluency guard", "STYLE_GAMING", why)
    return CheckResult("fluency guard", "PASS")


def preservation_check(package, v0, current, paragraph_id, text):
    """Guan Hong's deterministic rules: structure, citations, numbers, maths and protected terms."""
    candidate = with_paragraph(current, paragraph_id, text)
    references = (v0,) if current == v0 else (v0, current)
    verdict = deterministic(package, candidate, references)
    return CheckResult("preservation rules", verdict.status, "; ".join(verdict.reasons))


def is_proposal_only(package, paragraph_obj):
    kinds = {c.claim_id: c.kind for c in package.claims}
    return all(kinds.get(cid) == "proposal" for cid in paragraph_obj.claim_ids)


def no_new_facts_check(package, v0, paragraph_id, text):
    """Rules that need no model: no new numbers, no invented results, no added certainty."""
    original = paragraph(v0, paragraph_id)
    before, after = plain(original.text), plain(text)
    new_numbers = Counter(NUMBERS.findall(after)) - Counter(NUMBERS.findall(before))
    if new_numbers:
        return CheckResult("no new facts", "UNSUPPORTED_ADDITION", f"new number(s): {', '.join(new_numbers)}")
    if is_proposal_only(package, original):
        added = len(RESULT_WORDS.findall(after)) - len(RESULT_WORDS.findall(before))
        if added > 0:
            return CheckResult("no new facts", "UNSUPPORTED_ADDITION",
                               "a proposed study now reads as if it reports a result")
    gained = certainty_words(after) - certainty_words(before)
    if gained:
        return CheckResult("no new facts", "MAJOR_DRIFT", f"claim made more certain: {', '.join(gained)}")
    return CheckResult("no new facts", "PASS")


# ---------------------------------------------------------------- evidence check
class EvidenceIndex:
    """Quotes the team collected for each cited paper (package excerpts + evidence table)."""

    def __init__(self, package, facts_file=FACTS_FILE):
        self.paper_of = {}
        for source in package.sources:
            match = ACL_ID.search(source.url)
            self.paper_of[source.source_id] = match.group(1) if match else source.source_id
        self.excerpts = {}
        for e in package.evidence:
            self.excerpts.setdefault(e.source_id, []).append(e.excerpt)
        self.facts = {}
        if Path(facts_file).exists():
            table = pd.read_excel(facts_file, sheet_name="Master")
            for row in table.itertuples():
                self.facts.setdefault(str(row.paper_id), []).append(
                    {"fact": str(row.factual_claim), "quote": str(row.evidence_quote)})

    def for_text(self, text):
        out = []
        for source_id in dict.fromkeys(CITATION.findall(text)):
            paper = self.paper_of.get(source_id, source_id)
            out.append({"citation": source_id, "paper_id": paper,
                        "package_excerpts": self.excerpts.get(source_id, []),
                        "evidence_table": self.facts.get(paper, [])})
        return out


EVIDENCE_INSTRUCTIONS = """You check one rewritten paragraph of a research proposal against evidence.
You get the original paragraph, the rewrite, and for each cited paper the quotes the team
collected. Judge only the factual content of the rewrite, not its style.
For every sentence of the rewrite that describes what a cited paper did or found, decide
SUPPORTED (the quotes back it), UNSUPPORTED (no quote backs it, or it goes beyond them) or
CONTRADICTED (a quote says otherwise). Sentences about the authors' own proposed study are
NOT_A_SOURCE_CLAIM. Quote the evidence you relied on.
Set status to PASS unless the rewrite has a sentence that is UNSUPPORTED or CONTRADICTED
while the matching sentence in the original was supported. Problems already present in the
original are not the rewrite's fault: list them in pre_existing instead. If the evidence is
too thin to decide, use CHECK_ERROR."""

EVIDENCE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["status", "sentences", "reasons", "pre_existing"],
    "properties": {
        "status": {"type": "string", "enum": ["PASS", "UNSUPPORTED_ADDITION", "MAJOR_DRIFT", "CHECK_ERROR"]},
        "sentences": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["sentence", "label", "evidence"],
            "properties": {"sentence": {"type": "string"},
                           "label": {"type": "string",
                                     "enum": ["SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "NOT_A_SOURCE_CLAIM"]},
                           "evidence": {"type": "string"}}}},
        "reasons": {"type": "array", "items": {"type": "string"}},
        "pre_existing": {"type": "array", "items": {"type": "string"}},
    },
}


class EvidenceGate:
    """LLM check of cited claims against the evidence table. Only runs where a paragraph cites sources."""

    def __init__(self, provider, index, max_output_tokens=4000):
        self.provider, self.index, self.max_output_tokens = provider, index, max_output_tokens
        self.model = provider.model

    def check(self, original_text, text):
        evidence = self.index.for_text(original_text)
        if not evidence:
            return CheckResult("evidence check", "PASS", "no cited sources in this paragraph")
        payload = {"original": original_text, "rewrite": text, "evidence": evidence}
        try:
            result = self.provider.generate("evidence", EVIDENCE_INSTRUCTIONS, payload, EVIDENCE_SCHEMA,
                                            self.max_output_tokens)
            status = result["status"]
            if status not in EVIDENCE_SCHEMA["properties"]["status"]["enum"]:
                raise ValueError(f"unknown status {status!r}")
        except Exception as error:  # a failed check must never count as a pass
            return CheckResult("evidence check", "CHECK_ERROR", f"{type(error).__name__}: {error}")
        bad = [s for s in result["sentences"] if s["label"] in ("UNSUPPORTED", "CONTRADICTED")]
        reason = "; ".join(result["reasons"]) or "; ".join(f'{s["label"].lower()}: "{s["sentence"][:90]}"' for s in bad)
        return CheckResult("evidence check", status, reason)


def semantic_check(gate, package, v0, current, paragraph_id, text):
    """Guan Hong's LLM meaning check over the whole draft (catches context changes)."""
    candidate = with_paragraph(current, paragraph_id, text)
    references = (v0,) if current == v0 else (v0, current)
    verdict = gate.check(package, candidate, references)
    return CheckResult("meaning check", verdict.status, "; ".join(verdict.reasons))


# ---------------------------------------------------------------- all checks in order
def check_rewrite(package, v0, current, paragraph_id, text, *, evidence_gate=None, semantic_gate=None):
    """Run every check in order and return the list of results up to the first failure."""
    before = paragraph(current, paragraph_id).text
    results = []
    for run in (lambda: fluency_check(before, text),
                lambda: preservation_check(package, v0, current, paragraph_id, text),
                lambda: no_new_facts_check(package, v0, paragraph_id, text),
                (lambda: evidence_gate.check(paragraph(v0, paragraph_id).text, text)) if evidence_gate else None,
                (lambda: semantic_check(semantic_gate, package, v0, current, paragraph_id, text))
                if semantic_gate else None):
        if run is None:
            continue
        result = run()
        results.append(result)
        if not result.passed:
            break
    return results


def summary(results):
    """One line for reports: the check that rejected a rewrite, or 'passed all checks'."""
    failed = [r for r in results if not r.passed]
    if failed:
        return f"rejected by {failed[0].check}: {failed[0].reason or failed[0].status}"
    return "passed all checks (" + ", ".join(r.check for r in results) + ")"


def as_dicts(results):
    return [{"check": r.check, "status": r.status, "reason": r.reason} for r in results]


if __name__ == "__main__":
    print(json.dumps({"checks": ["length and tokens", "fluency guard", "preservation rules", "no new facts",
                                 "evidence check (LLM, optional)", "meaning check (LLM, optional)"]}, indent=2))
