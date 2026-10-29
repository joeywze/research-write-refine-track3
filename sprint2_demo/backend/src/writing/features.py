"""Measure writing features for analysis without turning them into edit rules."""

from collections import Counter
import re
from statistics import pvariance, pstdev

from .contracts import CITATION, SECTIONS

FEATURE_VERSION = "measurements-0.1"
WORDS = re.compile(r"\b[\w]+(?:[-'][\w]+)*\b")
HEDGES = ("may", "might", "could", "possibly", "perhaps", "potentially", "suggests",
          "appears to", "seems to", "likely", "unlikely")
TRANSITIONS = ("moreover", "furthermore", "in addition", "it is important to note", "it is worth noting")


def phrases(prose, vocabulary):
    return {phrase: count for phrase in vocabulary
            if (count := len(re.findall(r"\b" + re.escape(phrase) + r"\b", prose, re.I)))}


def measure_paragraph(prose):
    prose = CITATION.sub("", prose)
    words = WORDS.findall(prose)
    sentences = [WORDS.findall(s) for s in re.split(r"[.!?]+(?:\s+|$)", prose) if WORDS.search(s)]
    lengths = [len(s) for s in sentences]
    # Count trigrams within sentences.
    grams = Counter(" ".join(w.lower() for w in sentence[i:i + 3])
                    for sentence in sentences for i in range(len(sentence) - 2))
    repeated = {gram: count for gram, count in sorted(grams.items()) if count > 1}
    hedge_counts = phrases(prose, HEDGES)
    return {"word_count": len(words), "sentence_count": len(lengths),
            "sentence_length_variance": pvariance(lengths) if len(lengths) >= 2 else None,
            "sentence_length_cv": pstdev(lengths) / (sum(lengths) / len(lengths)) if len(lengths) >= 4 else None,
            "hedges": hedge_counts,
            "hedge_occurrences_per_100_words": 100 * sum(hedge_counts.values()) / len(words) if words else None,
            "repeated_trigrams": repeated,
            "repeated_trigram_excess": sum(count - 1 for count in repeated.values()),
            "transition_occurrences": phrases(prose, TRANSITIONS),
            "adjective_density": None,
            "adjective_density_status": "DEFERRED_REQUIRES_VALIDATED_POS_TAGGER"}


def measure(draft):
    paragraphs = [{"paragraph_id": p.paragraph_id, "section": p.section, **measure_paragraph(p.text)}
                  for p in draft.paragraphs]
    regularity = {}
    for section in SECTIONS:
        lengths = [p["word_count"] for p in paragraphs if p["section"] == section]
        regularity[section] = {"paragraph_count": len(lengths),
                               "paragraph_length_cv": (pstdev(lengths) / (sum(lengths) / len(lengths))
                                                       if len(lengths) >= 3 and sum(lengths) else None)}
    return {"version": FEATURE_VERSION, "status": "MEASUREMENT_ONLY_UNCALIBRATED",
            "affects_score_or_targets": False,
            "limitations": ["Sentence boundaries and hedge phrases use simple English rules.",
                            "Hedge counts include both necessary and redundant qualifications.",
                            "Repeated terms and similar paragraph lengths may suit the passage.",
                            "Compare similar sections. These measurements do not establish authorship."],
            "paragraphs": paragraphs, "section_regularity": regularity}
