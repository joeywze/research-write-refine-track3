"""Count possible style issues using three provisional rules."""

from dataclasses import dataclass
import re
from statistics import pstdev

from .contracts import CITATION, Draft
from .features import measure

DIAGNOSTIC_VERSION = "surface-0.1"
WORDS = re.compile(r"\b[\w]+(?:[-'][\w]+)*\b")
TRANSITIONS = ("moreover", "furthermore", "in addition", "it is important to note", "it is worth noting")


@dataclass(frozen=True)
class DiagnosticConfig:
    min_words: int = 20
    long_sentence_words: int = 35
    uniformity_min_sentences: int = 4
    uniformity_cv: float = 0.10
    transition_threshold: int = 2

    def __post_init__(self):
        if self.min_words < 1 or self.long_sentence_words < 1 or self.uniformity_min_sentences < 2:
            raise ValueError("Diagnostic count thresholds must be positive")
        if not 0 <= self.uniformity_cv <= 1 or self.transition_threshold < 2:
            raise ValueError("Invalid diagnostic thresholds")


def diagnose(draft: Draft, config: DiagnosticConfig = DiagnosticConfig()) -> dict:
    paragraphs, total, word_total = [], 0, 0
    for paragraph in draft.paragraphs:
        prose = CITATION.sub("", paragraph.text)
        words = WORDS.findall(prose)
        sentences = [WORDS.findall(s) for s in re.split(r"[.!?]+(?:\s+|$)", prose) if WORDS.search(s)]
        lengths = [len(s) for s in sentences]
        issues = []
        eligible = len(words) >= config.min_words
        transitions = sum(len(re.findall(r"\b" + re.escape(t) + r"\b", prose.lower())) for t in TRANSITIONS)
        long_count = sum(n > config.long_sentence_words for n in lengths)
        cv = pstdev(lengths) / (sum(lengths) / len(lengths)) if len(lengths) >= config.uniformity_min_sentences else None
        if eligible:
            if long_count:
                issues.append({"code": "LONG_SENTENCE", "count": long_count,
                               "evidence": {"sentence_lengths": lengths},
                               "advice": "Split a long sentence where its logical relationships can stay clear."})
            if transitions >= config.transition_threshold:
                issues.append({"code": "REPEATED_TRANSITIONS", "count": transitions - config.transition_threshold + 1,
                               "evidence": {"transition_occurrences": transitions},
                               "advice": "Remove a redundant transition if the connection is already clear."})
            if cv is not None and cv < config.uniformity_cv:
                issues.append({"code": "UNIFORM_LENGTH", "count": 1,
                               "evidence": {"sentence_length_cv": cv},
                               "advice": "Check whether varying sentence structure would make the passage clearer."})
        burden = sum(issue["count"] for issue in issues)
        total += burden
        word_total += len(words)
        paragraphs.append({"paragraph_id": paragraph.paragraph_id, "section": paragraph.section,
                           "word_count": len(words), "sentence_count": len(sentences),
                           "applicable": eligible, "uniformity_applicable": eligible and cv is not None,
                           "issue_count": burden, "issues": issues})
    applicable = any(p["applicable"] for p in paragraphs)
    return {"version": DIAGNOSTIC_VERSION, "direction": "lower_is_better",
            "score_label": "Review points flagged by rules",
            "interpretation": "Count of rule-based review points; lower is better. These rules still need calibration.",
            "applicable": applicable, "score": total if applicable else None,
            "word_count": word_total, "paragraphs": paragraphs,
            "exploratory_measurements": measure(draft)}


def targets(report: dict) -> tuple[str, ...]:
    qualitative = {p["paragraph_id"] for p in report.get("qualitative_critic", {}).get("paragraphs", [])
                   if any(f["status"] == "ACTIONABLE" for f in p["findings"])}
    return tuple(p["paragraph_id"] for p in report["paragraphs"]
                 if p["issues"] or p["paragraph_id"] in qualitative)
