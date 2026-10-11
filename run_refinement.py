#to run the complete pipeline, execute: python run_refinement.py

from src.refinement.io_utils import load_paper
from src.refinement.pipeline import run_refinement


if __name__ == "__main__":
    input_file = "data/generated/paper1.md" #to rename file accordingly
    n_iterations = 3

    original_paper = load_paper(input_file)

    result = run_refinement(
        original_paper=original_paper,
        n_iterations=n_iterations,
        output_dir="outputs",
    )

    print("\nRefinement complete.")

    print("\nBaseline metrics:")
    print(result["baseline_metrics"])

    print("\nFinal paper saved to:")
    print("outputs/final/revised_paper.md")

    print("\nMetrics saved to:")
    print("outputs/metrics.csv")

    print("\nIteration history saved to:")
    print("outputs/history.json")