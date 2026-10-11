# function: extract stylistic features, calculate a score, and give feedback


import json
import re
import statistics
from collections import Counter

from .llm_client import generate_text


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Common expressions worth reviewing when they are overused.
# Their presence alone does not mean the writing is poor.
GENERIC_PHRASES = [
    "it is important to note that",
    "it is worth noting that",
    "plays a crucial role",
    "plays a vital role",
    "in today's rapidly evolving",
    "in the ever-changing landscape",
    "underscores the importance of",
    "delve into",
    "multifaceted",
    "comprehensive understanding",
    "furthermore",
    "moreover",
    "in conclusion",
    "in summary",
]

HEDGE_PATTERNS = [
    r"\bmay\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\bpossibly\b",
    r"\bperhaps\b",
    r"\bsuggests?\b",
    r"\bappears to\b",
    r"\blikely\b",
    r"\bpotentially\b",
]


# ============================================================
# 2. TEXT PROCESSING
# ============================================================

def tokenize_sentences(text: str) -> list[str]:
    """Split text into approximate sentences."""
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def tokenize_words(text: str) -> list[str]:
    """Extract words and normalize them to lowercase."""
    return re.findall(r"\b[\w'-]+\b", text.lower())


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Restrict a number to a specified range."""
    return max(minimum, min(value, maximum))


# ============================================================
# 3. EXTRACT STYLISTIC FEATURES
# ============================================================

def extract_stylistic_features(text: str) -> dict:
    """
    Extract interpretable stylistic features from a paper.

    These features describe writing patterns. They are not
    reliable indicators of whether a text was written by AI.
    """
    if not text.strip():
        raise ValueError("Paper cannot be empty.")

    sentences = tokenize_sentences(text)
    words = tokenize_words(text)

    word_count = len(words)
    sentence_count = len(sentences)

    sentence_lengths = [
        len(tokenize_words(sentence))
        for sentence in sentences
    ]

    mean_length = (
        statistics.mean(sentence_lengths)
        if sentence_lengths else 0.0
    )

    length_sd = (
        statistics.pstdev(sentence_lengths)
        if len(sentence_lengths) > 1 else 0.0
    )

    length_cv = (
        length_sd / mean_length
        if mean_length > 0 else 0.0
    )

    # Repeated adjacent word pairs.
    bigrams = list(zip(words, words[1:]))
    bigram_counts = Counter(bigrams)

    repeated_bigram_count = sum(
        count - 1
        for count in bigram_counts.values()
        if count > 1
    )

    repetition_rate = (
        repeated_bigram_count / len(bigrams)
        if bigrams else 0.0
    )

    # Count generic phrases and their approximate frequency.
    lower_text = text.lower()

    generic_phrase_counts = {
        phrase: len(
            re.findall(re.escape(phrase), lower_text)
        )
        for phrase in GENERIC_PHRASES
    }

    generic_phrase_count = sum(
        generic_phrase_counts.values()
    )

    generic_phrases_per_1000_words = (
        generic_phrase_count / word_count * 1000
        if word_count else 0.0
    )

    # Repeated sentence openings.
    sentence_starts = []

    for sentence in sentences:
        sentence_words = tokenize_words(sentence)

        if sentence_words:
            sentence_starts.append(
                " ".join(sentence_words[:2])
            )

    start_counts = Counter(sentence_starts)

    repeated_start_count = sum(
        count - 1
        for count in start_counts.values()
        if count > 1
    )

    repeated_start_rate = (
        repeated_start_count / sentence_count
        if sentence_count else 0.0
    )

    # Long sentences that may deserve manual review.
    long_sentence_count = sum(
        length > 35
        for length in sentence_lengths
    )

    long_sentence_rate = (
        long_sentence_count / sentence_count
        if sentence_count else 0.0
    )

    # Hedging is reported for review, not automatically penalized.
    hedge_count = sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in HEDGE_PATTERNS
    )

    hedge_rate = (
        hedge_count / word_count * 100
        if word_count else 0.0
    )

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "mean_sentence_length": round(mean_length, 2),
        "sentence_length_sd": round(length_sd, 2),
        "sentence_length_cv": round(length_cv, 3),
        "bigram_repetition_rate": round(repetition_rate, 4),
        "generic_phrase_count": generic_phrase_count,
        "generic_phrases_per_1000_words": round(
            generic_phrases_per_1000_words, 2
        ),
        "generic_phrase_details": {
            phrase: count
            for phrase, count in generic_phrase_counts.items()
            if count > 0
        },
        "repeated_sentence_start_rate": round(
            repeated_start_rate, 3
        ),
        "long_sentence_rate": round(long_sentence_rate, 3),
        "hedges_per_100_words": round(hedge_rate, 3),
    }


# ============================================================
# 4. CALCULATE A TRANSPARENT STYLE SCORE
# ============================================================

def calculate_style_score(features: dict) -> dict:
    """
    Calculate a heuristic writing-style diagnostic score from
    0 to 100.

    Higher means fewer selected surface-level warning signals.
    This is NOT an AI-authorship probability or an overall
    measure of academic quality.

    The weights are initial design choices, not empirically
    validated weights.
    """
    penalties = {}

    # Repeated word pairs: up to 25 penalty points.
    penalties["repetition"] = (
        25 * clamp(
            features["bigram_repetition_rate"] / 0.08,
            0.0,
            1.0,
        )
    )

    # Generic phrase frequency: up to 20 penalty points.
    penalties["generic_phrases"] = (
        20 * clamp(
            features["generic_phrases_per_1000_words"] / 10,
            0.0,
            1.0,
        )
    )

    # Repeated sentence openings: up to 15 points.
    penalties["repeated_openings"] = (
        15 * clamp(
            features["repeated_sentence_start_rate"] / 0.30,
            0.0,
            1.0,
        )
    )

    # Excessively long sentences: up to 15 points.
    penalties["long_sentences"] = (
        15 * clamp(
            features["long_sentence_rate"] / 0.40,
            0.0,
            1.0,
        )
    )

    # Sentence-length variation: up to 10 points.
    # Very low variation may indicate monotonous structure.
    # Very high variation can also indicate inconsistent prose.
    cv = features["sentence_length_cv"]

    if cv < 0.25:
        variation_penalty = 10 * clamp(
            (0.25 - cv) / 0.25,
            0.0,
            1.0,
        )
    elif cv > 1.20:
        variation_penalty = 10 * clamp(
            (cv - 1.20) / 0.80,
            0.0,
            1.0,
        )
    else:
        variation_penalty = 0.0

    penalties["sentence_variation"] = variation_penalty

    score = round(
        clamp(100 - sum(penalties.values()), 0, 100),
        2,
    )

    return {
        "style_score": score,
        "score_interpretation": (
            "Higher scores indicate fewer warning signals "
            "under this particular heuristic."
        ),
        "penalties": {
            name: round(value, 2)
            for name, value in penalties.items()
        },
    }


# ============================================================
# 5. GENERATE CONSTRUCTIVE FEEDBACK
# ============================================================

def generate_feedback(paper: str) -> dict:
    """
    Analyze a paper, calculate its style score, and generate
    constructive feedback for the revision function.

    Returns:
        {
            "features": {...},
            "score": {...},
            "feedback": "..."
        }
    """
    if not paper.strip():
        raise ValueError("Paper cannot be empty.")

    # A. Extract measurable stylistic features.
    features = extract_stylistic_features(paper)

    # B. Calculate the heuristic score.
    score = calculate_style_score(features)

    # C. Give the LLM measured evidence for its review.
    analysis = {
        "features": features,
        "score": score,
    }

    prompt = """
You are an academic writing reviewer helping improve a research paper.

Review the paper using BOTH the measured stylistic features and
your assessment of the actual argument and prose.

MEASURED FEATURES AND SCORE:
__ANALYSIS__

PAPER:
__PAPER__

Your task is to produce constructive feedback for a separate
rewriting function.

Evaluate:
1. Repetitive phrases and sentence openings.
2. Sentence structure and readability.
3. Generic statements that lack specific reasoning.
4. Weak transitions or unclear logical connections.
5. Claims that are too broad or insufficiently supported.
6. Whether uncertainty and limitations are expressed appropriately.
7. Whether the paper explains its contribution clearly.

Requirements:
- Identify concrete examples from the paper.
- Prioritize the five most important improvements.
- Explain why each proposed change would help.
- Recommend a specific revision action for each problem.
- Distinguish genuine problems from acceptable academic conventions.
- Do not assume a feature is bad simply because its numerical value
  is high or low.
- Do not target an AI detector or try to disguise authorship.
- Do not invent references, experiments, evidence or results.
- Preserve scientific meaning, technical terminology and citations.
- Do not recommend adding hedging unless the claim's certainty
  actually exceeds the available evidence.
- If a measured feature does not reveal a real writing problem,
  explicitly say that no change is necessary for that feature.

Return your answer in this format:

OVERALL ASSESSMENT
Briefly describe the main strengths and weaknesses.

PRIORITIZED FEEDBACK
For each recommendation, provide:
- Priority
- Issue
- Evidence from the paper
- Recommended revision
- Reason for the recommendation

PRESERVATION REQUIREMENTS
List claims, numbers, citations, technical details and limitations
that must remain unchanged.

HUMAN REVIEW FLAGS
Identify any scientific or factual issues that cannot be resolved
through stylistic rewriting alone.

Do not rewrite the paper itself. The separate revision function
will use your feedback.
"""

    # Replace placeholders instead of str.format(), so braces
    # in the prompt or serialized JSON cannot cause formatting errors.
    prompt = (
        prompt
        .replace("__ANALYSIS__", json.dumps(
            analysis, ensure_ascii=False, indent=2
        ))
        .replace("__PAPER__", paper)
    )

    feedback_text = generate_text(prompt)

    if not feedback_text.strip():
        raise RuntimeError("The feedback generator returned no text.")

    return {
        "features": features,
        "score": score,
        "feedback": feedback_text,
    }
