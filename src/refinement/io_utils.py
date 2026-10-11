#function: load and save drafts and logs

from pathlib import Path


def load_paper(file_path: str) -> str:
    """Load a Markdown or plain-text paper."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Paper not found: {file_path}"
        )

    paper = path.read_text(encoding="utf-8")

    if not paper.strip():
        raise ValueError("Input paper is empty.")

    return paper


def save_paper(paper: str, file_path: str) -> None:
    """Save a paper as UTF-8 text."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(paper, encoding="utf-8")