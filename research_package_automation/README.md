# Research package automation

This backend prototype takes a topic and selected PDFs, extracts candidate evidence,
and exports a research package and a matching Master fact sheet. It is intended
for the teammates building the interface to call from their application.

## Files

| File | Purpose |
|---|---|
| `research_package_builder.py` | Read PDFs, extract evidence and generate the package and workbook |
| `evidence_checker.py` | Retrieve supporting excerpts and generate fresh draft verdicts |
| `support/` | Package/draft contracts, JSON response schemas, API token budget and run storage |
| `test_backend.py` | Offline integration and source-integrity tests with synthetic model responses |
| `requirements.txt` | Dependencies for this folder |

The support code is adapted from the repository's `main` branch at commit
`5890e1067c1910bb178c20083a2e756f6cd9f815`. It is bundled here because the
`research-idea` branch has an older layout. The package/draft schema remains 0.1.

## Try it from the repository root

```bash
python -m pip install -r research_package_automation/requirements.txt
python -m unittest research_package_automation.test_backend -v
```

Set `OPENAI_API_KEY` in your local environment or root `.env`. Then substitute
an available model ID and real PDF paths below. Calls send the extracted text
to the API and share the selected token allowance across the run.

```bash
python -m research_package_automation.research_package_builder \
  --topic "Your research question" \
  --pdf /path/to/paper1.pdf /path/to/paper2.pdf \
  --model YOUR_MODEL \
  --output /path/to/new-project-output
```

This writes `research_package.json`, `master_facts.xlsx`, `source_text.json`,
`rejected_evidence.json`, model-call events and a completion manifest. Each run
requires a new output directory. Keep generated outputs outside version control.
A completed package has a `build_manifest.json` with status `COMPLETED`.

Add `--with-draft --checker-model YOUR_CHECKING_MODEL` to generate V0 and check
its claims. Choose a different checking model. This also writes `v0.json`,
`draft_v0.md`, `fact_check_results.json` and `draft_manifest.json`. The checking
step creates fresh judgments against the generated evidence sheet.

To check a later schema 0.1 draft, run the following command.

```bash
python -m research_package_automation.evidence_checker \
  --package /path/to/project/research_package.json \
  --draft /path/to/v0.json \
  --facts /path/to/project/master_facts.xlsx \
  --model YOUR_CHECKING_MODEL \
  --scope cited-literature \
  --output /path/to/new-check-output
```

The `cited-literature` scope checks only paragraphs containing source citations,
maps each extracted factual claim to the exact cited source IDs selected for it,
and reports uncited paragraphs as skipped instead of evidence failures. Use
`--scope all` when the goal is to audit every factual assertion in the draft.

## Connect from the interface

Call these functions from the repository root or with the repository on the
Python module path. Create a new output directory for each user project.

```python
from pathlib import Path
from research_package_automation.research_package_builder import (
    read_pdfs, build_research_package, generate_and_check,
)
from research_package_automation.support.providers import OpenAIJSON, TokenBudget
from research_package_automation.support.storage import RunStore

papers = read_pdfs(pdf_paths)
store = RunStore(Path(output_directory))
budget = TokenBudget(200_000)
writer = OpenAIJSON(writer_model, budget, store, stage="research_package")
package = build_research_package(topic, papers, writer, store)

# After the user reviews the package, optionally generate and check V0.
checker = OpenAIJSON(checker_model, budget, store, stage="fact_checking")
draft, verdicts = generate_and_check(
    package, store.directory / "master_facts.xlsx", writer, checker, store,
)
```

For a subsequent drafting attempt, use a new RunStore directory so previously
saved output stays consistent. The Excel `Master` sheet has the existing columns
`claim_id`, `paper_id`, `title`, `factual_claim`, `evidence_quote`, `page`,
`verification`, `source_url`, `contributor`, `language_evidence` and
`review_boundary`.

The workbook and package come from the same evidence records. `load_facts()`
rejects a mismatched package/workbook pair. Tabitha can use the workbook through
her existing loader or review `check_draft()` for the fresh-verdict integration.
The new checker is a prototype extension for new projects and needs evaluation.

Uploads use `urn:sha256:...` source identifiers so the model does not invent
public source URLs. Display those identifiers as text and retain the original
PDFs for review. An interface that requires HTTPS source links will need to
support these uploaded-source identifiers or collect a real URL from the user.

Later, paper-search results can enter the same builder after obtaining their
text. Each paper record needs `paper_id`, `title`, `source_url` and
`pages`, with each page containing `page` and `text`. The extraction pipeline
currently starts with user-selected papers.

## Verification boundaries

The offline tests check data flow, source quotes, duplicate handling, workbook
consistency and fresh judgments. They use scripted responses and do not measure
LLM extraction or fact-checking accuracy. Live API testing with real papers is
still required.

Quotes must match the extracted page text after Unicode/whitespace
normalisation. Generated claims remain `UNREVIEWED` because a matching quote does
not establish correct interpretation. The draft checker retrieves up to three
passages from cited sources using TF-IDF and asks an LLM for `SUPPORTED`,
`CONTRADICTED` or `INSUFFICIENT_EVIDENCE`. Prospective work is recorded as
`PROPOSAL`. Extraction may omit or misclassify assertions, and retrieval may miss
the relevant passage, so evaluate these outputs against human-reviewed examples.

The prototype accepts 1–20 text-readable PDFs, each up to 25 MB. Scanned PDFs
need OCR. Candidate gaps are scoped to the selected papers and require a broader
literature check before novelty can be established.

## Export an existing reviewed topic

`export_reviewed_topic.py` converts an existing six-section Draft V0 and its
reviewed evidence tables to the same schema without regenerating the research.
Topic-specific scientific choices, including protected terms, live in a reviewed
`handover_config.json`; paragraph positions and citations are derived from the
draft rather than hard-coded.

```bash
python -m research_package_automation.export_reviewed_topic \
  drafts/track3_four_cluster_v0/cluster6 \
  drafts/track3_four_cluster_v0/cluster6/handover
```

The exporter writes `research_package.json`, `v0.json`, `master_facts.xlsx` and
an export manifest. The fact sheet retains every reviewed evidence passage for
each mapped source claim and is accepted by `evidence_checker.py`.
Existing reviewed drafts exported without retrospective approval are marked
`PROVISIONAL_AUTOMATED_MAPPING` and `production_ready: false`. They are suitable
for a clearly labelled demonstration, not final research sign-off. Schema
validation is not semantic approval.
