import os
import time
import pandas as pd
from openai import OpenAI

INPUT_FILE = "data/samples/sample_10_papers.csv"
OUTPUT_FILE = "data/generated/ai_generated_sections.csv"

MODEL = "gpt-5.6-luna"

SECTIONS = [
    "abstract",
    "introduction",
    "related_work",
    "methodology",
    "experiments",
    "conclusion"
]

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

df = pd.read_csv(INPUT_FILE)

results = []

for index, row in df.iterrows():

    print(f"Processing {index + 1}/{len(df)}: {row['title']}")

    for section in SECTIONS:

        prompt = f"""
You are writing a draft NLP research paper.

Title:
{row['title']}

Original abstract:
{row['abstract']}

Write only the {section.replace("_", " ")} section.

Requirements:
- Use academic research-paper style.
- Stay consistent with the title and abstract.
- Do not copy sentences directly from the abstract.
- Do not invent citations.
- Do not invent specific numerical results.
- If information is unavailable, keep it general.
"""

        response = client.responses.create(
            model=MODEL,
            input=prompt
        )

        results.append({
            "paper_id": row["paper_id"],
            "title": row["title"],
            "section": section,
            "text": response.output_text,
            "source_type": "ai",
            "model": MODEL,
            "prompt_version": "v1"
        })

        time.sleep(1)

output_df = pd.DataFrame(results)

output_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Saved {len(output_df)} generated sections to {OUTPUT_FILE}")