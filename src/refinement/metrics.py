#function: writing-quality measurements

import re
import statistics
from collections import Counter


def tokenize_sentences(text: str) -> list[str]:
    """Split text into approximate sentences."""
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def tokenize_words(text: str) -> list[str]:
    """Extract words for simple text analysis."""
    return re.findall(r"\b[\w'-]+\b", text.lower())


def measure_writing(text: str) -> dict:
    """
    Calculate basic stylistic measurements.

    These metrics describe surface-level text features.
    They do not establish whether a human or an AI wrote the text.
    """
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)

    sentence_lengths = [
        len(tokenize_words(sentence))
        for sentence in sentences
    ]

    word_count = len(words)
    sentence_count = len(sentences)

    length_mean = (
        statistics.mean(sentence_lengths)
        if sentence_lengths else 0.0
    )

    length_sd = (
        statistics.pstdev(sentence_lengths)
        if len(sentence_lengths) > 1 else 0.0
    )

    # Count repeated word bigrams as a basic repetition indicator.
    bigrams = list(zip(words, words[1:]))
    bigram_counts = Counter(bigrams)

    repeated_bigrams = sum(
        count - 1
        for count in bigram_counts.values()
        if count > 1
    )

    bigram_repetition_rate = (
        repeated_bigrams / len(bigrams)
        if bigrams else 0.0
    )

    # A small, transparent list of common academic hedging expressions.
    hedge_patterns = [
        r"\bmay\b",
        r"\bmight\b",
        r"\bcould\b",
        r"\bpossibly\b",
        r"\bsuggests?\b",
        r"\bappears to\b",
        r"\blikely\b",
    ]

    hedge_count = sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in hedge_patterns
    )

    hedge_rate_per_100_words = (
        hedge_count / word_count * 100
        if word_count else 0.0
    )

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "mean_sentence_length": round(length_mean, 3),
        "sentence_length_sd": round(length_sd, 3),
        "bigram_repetition_rate": round(
            bigram_repetition_rate, 4
        ),
        "hedges_per_100_words": round(
            hedge_rate_per_100_words, 3
        ),
    }