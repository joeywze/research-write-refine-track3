import pandas as pd

INPUT_FILE = "data/raw/emnlp2025_papers.csv"
OUTPUT_FILE = "data/samples/sample_10_papers.csv"

df = pd.read_csv(INPUT_FILE)

sample = df.sample(
    n=10,
    random_state=42
)

sample.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Saved {len(sample)} papers to {OUTPUT_FILE}")