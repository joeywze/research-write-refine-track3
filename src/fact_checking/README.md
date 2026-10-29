# Pilot evidence checking

Run from the repository root after installing root dependencies:

```sh
python src/fact_checking/fact_checker.py
```

The previous `python src/fact_checker.py` command remains a compatibility launcher.

## Inputs and outputs

- Research draft: [docs/research/draft_v0.md](../../docs/research/draft_v0.md).
- Evidence database: `data/facts/master_facts.xlsx`, sheet `Master`.
- Pilot claims and saved assessments: `data/facts/pilot/`.
- Retrieved evidence report: `results/fact_checking/draft_v0_evidence_matches.csv`.

The script extracts candidate sentences and table claims, applies baseline claim classification and retrieves evidence using TF-IDF/cosine similarity. It also reads the saved manual pilot assessments and reports the fraction labelled `SUPPORTED`.

That fraction describes the seven assessed pilot claims only. Retrieval relevance is not factual support. Running the script does not perform new semantic verification or update the manual support labels. It checks for an API key but does not thereby establish that an AI verification request was made.

Execution can download NLTK tokenizer data and replace the matching CSV. This legacy script has top-level side effects; do not import it in the UI or a test discovery process. The cleanup only changes its repository root and draft path, not its claim labels or scoring method.
