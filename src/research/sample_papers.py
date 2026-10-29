from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data/emnlp_2025_main.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data/samples/sample_10_papers.csv"

df = pd.read_excel(INPUT_FILE)

sample = df.sample(
    n=10,
    random_state=42
)

sample.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Saved {len(sample)} papers to {OUTPUT_FILE}")
