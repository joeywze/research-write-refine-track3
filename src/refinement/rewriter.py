# function: rewrite a draft while preserving its claims and citations

from .llm_client import generate_text
from .prompts import REWRITE_PROMPT


def revise_paper(paper: str, feedback: str) -> str:
    """
    Revise a paper using the feedback generated in Function 1.

    Args:
        paper: Current paper version.
        feedback: Feedback for the current paper.

    Returns:
        Complete revised paper.
    """
    if not paper.strip():
        raise ValueError("Paper cannot be empty.")

    if not feedback.strip():
        raise ValueError("Feedback cannot be empty.")

    prompt = REWRITE_PROMPT.format(
        paper=paper,
        feedback=feedback,
    )

    revised_paper = generate_text(prompt)

    if not revised_paper:
        raise RuntimeError("The revision generator returned no text.")

    return revised_paper