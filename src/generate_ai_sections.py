import os
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. Check that your .env file exists."
    )

client = OpenAI(api_key=api_key)

# --------------------------------------------------
# FILE PATHS AND SETTINGS
# --------------------------------------------------

INPUT_FILE = "data/samples/sample_10_papers.csv"
OUTPUT_FILE = "data/generated/ai_generated_sections_v1.csv"

MODEL = "gpt-5.6-luna"

SECTIONS = [
    "abstract",
    "introduction",
    "related_work",
    "methodology",
    "experiments",
    "conclusion"
]

# --------------------------------------------------
# LOAD INPUT DATA
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} papers.")

results = []

# --------------------------------------------------
# GENERATE SECTIONS
# --------------------------------------------------

for index, row in df.iterrows():

    print(
        f"\nProcessing {index + 1}/{len(df)}: "
        f"{row['title']}"
    )

    for section in SECTIONS:

        print(f"Generating {section}...")

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
- Do not copy sentences directly from the original abstract.
- Do not invent citations.
- Do not invent specific numerical results.
- If information is unavailable, keep the description general.
"""

        try:
            response = client.responses.create(
                model=MODEL,
                input=prompt
            )

            generated_text = response.output_text

            results.append({
                "paper_id": row["paper_id"],
                "title": row["title"],
                "section": section,
                "text": generated_text,
                "source_type": "ai",
                "model": MODEL,
                "prompt_version": "v1_abstract_grounded"
            })

            # Save progress after every successful section
            pd.DataFrame(results).to_csv(
                OUTPUT_FILE,
                index=False
            )

            print(f"Saved {section}.")

            # Small delay between API calls
            time.sleep(1)

        except Exception as e:
            print(
                f"Error generating {section} "
                f"for paper {row['paper_id']}: {e}"
            )

# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

output_df = pd.DataFrame(results)

print("\nGeneration complete.")
print(f"Generated {len(output_df)} sections.")
print(f"Output saved to: {OUTPUT_FILE}")

if not output_df.empty:
    print("\nSections generated:")
    print(output_df["section"].value_counts())