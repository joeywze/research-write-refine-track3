import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------
# PATHS AND SETTINGS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data/samples/sample_30_papers.csv"
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data/generated/ai_generated_sections_stratified_30_v1.csv"
)

MODEL = "gpt-5.6-luna"
PROMPT_VERSION = "v1_abstract_grounded"

SECTIONS = [
    "abstract",
    "introduction",
    "related_work",
    "methodology",
    "experiments",
    "conclusion",
]

OUTPUT_COLUMNS = [
    "paper_id",
    "title",
    "topic_family",
    "section",
    "text",
    "source_type",
    "model",
    "prompt_version",
]

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# LOAD INPUT AND VALIDATE
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE, keep_default_na=False)

required_columns = ["paper_id", "title", "abstract", "topic_family"]
missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Input CSV is missing columns: {sorted(missing_columns)}"
    )

for column in required_columns:
    if df[column].astype(str).str.strip().eq("").any():
        raise ValueError(f"Input CSV contains empty values in '{column}'.")

if df["paper_id"].duplicated().any():
    raise ValueError("Input CSV contains duplicate paper IDs.")

print(f"Loaded {len(df)} papers.")

# --------------------------------------------------
# LOAD PREVIOUS RESULTS FOR RESUMING
# --------------------------------------------------

results = []

if OUTPUT_FILE.exists():
    saved = pd.read_csv(OUTPUT_FILE, keep_default_na=False)

    missing_output_columns = set(OUTPUT_COLUMNS) - set(saved.columns)
    if missing_output_columns:
        raise ValueError(
            "Existing output is missing columns: "
            f"{sorted(missing_output_columns)}"
        )

    if (
        saved["model"].ne(MODEL).any()
        or saved["prompt_version"].ne(PROMPT_VERSION).any()
    ):
        raise ValueError(
            "Existing output uses a different model or prompt version. "
            "Choose a different OUTPUT_FILE."
        )

    if not set(saved["paper_id"]).issubset(set(df["paper_id"])):
        raise ValueError(
            "Existing output contains papers outside this input sample. "
            "Choose a different OUTPUT_FILE."
        )

    if not set(saved["section"]).issubset(set(SECTIONS)):
        raise ValueError("Existing output contains unexpected section names.")

    # Empty sections will be regenerated.
    saved = saved[saved["text"].astype(str).str.strip().ne("")]

    if saved.duplicated(["paper_id", "section"]).any():
        raise ValueError(
            "Existing output contains duplicate paper/section pairs."
        )

    results = saved[OUTPUT_COLUMNS].to_dict("records")
    print(f"Resuming with {len(results)} saved sections.")

completed = {
    (result["paper_id"], result["section"])
    for result in results
}

# --------------------------------------------------
# LOAD API KEY
# --------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. Check the project's .env file."
    )

client = OpenAI(api_key=api_key)

# --------------------------------------------------
# GENERATE SECTIONS
# --------------------------------------------------

failures = []

for index, row in df.iterrows():
    print(f"\nProcessing {index + 1}/{len(df)}: {row['title']}")

    for section in SECTIONS:
        key = (row["paper_id"], section)

        if key in completed:
            print(f"Skipping saved section: {section}")
            continue

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
                input=prompt,
            )

            generated_text = (response.output_text or "").strip()

            if not generated_text:
                raise ValueError("The model returned empty text.")

        except Exception as error:
            failures.append(key)
            print(
                f"Error generating {section} "
                f"for {row['paper_id']}: {error}"
            )
            continue

        results.append({
            "paper_id": row["paper_id"],
            "title": row["title"],
            "topic_family": row["topic_family"],
            "section": section,
            "text": generated_text,
            "source_type": "ai",
            "model": MODEL,
            "prompt_version": PROMPT_VERSION,
        })

        # Write to a temporary file, then replace the output.
        # Save failures stop execution instead of being silently ignored.
        temporary_file = OUTPUT_FILE.with_suffix(".tmp")
        pd.DataFrame(results, columns=OUTPUT_COLUMNS).to_csv(
            temporary_file,
            index=False,
        )
        os.replace(temporary_file, OUTPUT_FILE)

        completed.add(key)
        print(f"Saved {section}.")
        time.sleep(1)

# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

output_df = pd.DataFrame(results, columns=OUTPUT_COLUMNS)
expected = len(df) * len(SECTIONS)

print("\nGeneration run finished.")
print(f"Saved sections: {len(output_df)}/{expected}")
print(f"Failed requests this run: {len(failures)}")

if not output_df.empty:
    print(f"Output: {OUTPUT_FILE}")
    print("\nSections saved:")
    print(output_df["section"].value_counts())

if len(output_df) < expected:
    print("\nRestart the script to retry missing sections.")