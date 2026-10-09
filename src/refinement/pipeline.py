"""Run and log iterative paper refinement."""

import csv
import json
from pathlib import Path

from .feedback import (
    calculate_style_score,
    extract_stylistic_features,
    generate_feedback,
)
from .metrics import measure_writing
from .rewriter import revise_paper


def measure_draft(text: str) -> dict:
    """Combine writing metrics with the heuristic style score."""
    metrics = measure_writing(text)
    score = calculate_style_score(extract_stylistic_features(text))
    metrics["style_score"] = (
        score["style_score"] if isinstance(score, dict) else score
    )
    return metrics


def run_refinement(
    original_paper: str,
    n_iterations: int = 3,
    output_dir: str = "outputs",
) -> dict:
    """Refine a paper iteratively and save drafts, feedback, and metrics."""
    if not original_paper.strip():
        raise ValueError("Original paper cannot be empty.")
    if n_iterations < 0:
        raise ValueError("n_iterations must be non-negative.")

    output_path = Path(output_dir)
    iteration_path = output_path / "iterations"
    final_path = output_path / "final"
    iteration_path.mkdir(parents=True, exist_ok=True)
    final_path.mkdir(parents=True, exist_ok=True)

    current_paper = original_paper
    history = []
    baseline = measure_draft(original_paper)

    with (output_path / "metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["iteration", *baseline.keys()],
        )
        writer.writeheader()
        writer.writerow({"iteration": 0, **baseline})

        for iteration in range(1, n_iterations + 1):
            print(f"Starting refinement iteration {iteration}/{n_iterations}")

            result = generate_feedback(current_paper)
            feedback = result.get("feedback", "") if isinstance(result, dict) else result
            if not isinstance(feedback, str) or not feedback.strip():
                raise ValueError("Feedback generator returned no feedback.")

            revised_paper = revise_paper(current_paper, feedback)
            metrics = measure_draft(revised_paper)

            iteration_dir = iteration_path / f"iteration_{iteration}"
            iteration_dir.mkdir(parents=True, exist_ok=True)
            (iteration_dir / "feedback.md").write_text(feedback, encoding="utf-8")
            (iteration_dir / "draft.md").write_text(revised_paper, encoding="utf-8")

            history.append({
                "iteration": iteration,
                "feedback": feedback,
                "draft": revised_paper,
                "metrics": metrics,
            })
            writer.writerow({"iteration": iteration, **metrics})
            current_paper = revised_paper

    (final_path / "revised_paper.md").write_text(
        current_paper, encoding="utf-8"
    )
    (output_path / "history.json").write_text(
        json.dumps(
            {
                "n_iterations": n_iterations,
                "baseline_metrics": baseline,
                "history": history,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "original_paper": original_paper,
        "final_paper": current_paper,
        "baseline_metrics": baseline,
        "history": history,
    }