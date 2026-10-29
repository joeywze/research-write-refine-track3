# Track 3: Research Paper Ideation and Writing

This project uses published evidence to develop a research idea and draft a paper. Team A reviews the literature and approves the Research Package. Stage B writes or accepts an initial draft, identifies wording problems and revises selected paragraphs while checking that the content stays intact.

## Writing workflow

The module covers Abstract, Introduction, Related Work, Methodology, Experiments and Conclusion. For a proposed study, the experiments section describes the evaluation plan.

1. Check the Research Package and draft format.
2. Check the initial draft against the supplied evidence.
3. Identify paragraphs to revise.
4. Produce a generic rewrite and a guided rewrite from the same initial draft.
5. Allow up to three guided attempts, including rejected attempts.
6. Check each candidate against the package, original draft and last accepted version. Keep the last accepted draft if a candidate fails.
7. Save the drafts, diagnostics, checks, usage and timing.

Once the inputs and model credentials are supplied, these steps run automatically. Human review is available for assessing output quality and checker accuracy; it is not an approval step in the revision loop.

Use V0 for the initial draft, V1 for the final accepted generic rewrite and V2 for the final accepted guided draft. Comparing V2 with V1 assesses the complete workflow, including its extra computation. Comparing the first attempts assesses feedback when both approaches edit the same paragraphs once.

## Scores and critic

The main method combines **Rule-based checks** and **LLM writing review**. Reports show **Review points flagged by rules** and **Review points flagged by the LLM**. A review point marks something to consider; it does not necessarily lead to an edit. Lower counts mean fewer review points, not a higher overall quality mark or a different authorship estimate.

The module also records sentence-length variance, hedge frequency, repeated trigrams and paragraph-length regularity for analysis. These measurements do not trigger edits. Adjective density is deferred until a suitable part-of-speech tagger has been tested.

Rule-based checks count long sentences, repeated transitions and unusually uniform sentence lengths. LLM writing review identifies passages that could benefit from clearer, more precise, better-connected or more natural wording. Each point eligible for revision includes a quote, explanation and suggested change. Problems that need more evidence are recorded for review.

The LLM uses six detailed criteria: specificity, argument strength, formulaic language, inappropriate hedging, generic transitions and unnatural symmetry. Its count is the number of actionable paragraph-criterion findings, which can exceed six across a full paper. Both methods may flag the same passage, so their counts remain separate.
## Cluster 7 Source Evidence Review

The [source-cited review of all 18 Cluster 7 papers](docs/cluster7_source_evidence_review.md)
records 52 short author quotations with PDF page and section links. Each quotation
was checked against the saved extracted text and the local paper PDF. The
[verification manifest](data/processed/cluster7_source_evidence_manifest.json)
records paper IDs, source hashes, page locations and quotation hashes.

This is a targeted source-passage review, not an independent reproduction of the
papers' results or approval of a research-gap claim. Dimensions not established by
the cited evidence remain unclear. The original automated review files are retained.

## Part A Research Development and Provisional V0

The [working Part A handover](docs/part_a_research_development/README.md) follows
the literature-verification, evidence-table, candidate-gap and proposed-study steps.
It includes 18 claim records with 38 checked excerpts, external counterevidence,
an evaluation plan and a six-section provisional V0.

This is an evidence-backed proposal, not a completed experiment or a confirmed
novelty claim. Language selection, raters, data source, judge configuration and
Team A approval remain unresolved. The original automated review files are retained.


Guided candidates must pass preservation, avoid increasing either issue count and reduce at least one. Use `--method rules-only` to run the original three-rule comparison without the LLM critic. See [the writing guide](docs/stage_b.md) and [feature selection](docs/feature_selection.md) for details.

## Try the offline example

Python 3.10 or later is required. The tests and scripted example use only the standard library.

~~~text
python -m unittest discover -s tests -v
python -m src.writing validate --package examples/research_package.json --v0 examples/v0.json
python -m src.writing demo --output runs/synthetic-demo
python -m src.writing measure --package examples/research_package.json --v0 examples/v0.json --output runs/feature-review
python -m src.writing export-human --runs runs/synthetic-demo --output evaluation-output/synthetic-demo
~~~

Run commands from the repository root and choose a new output directory each time. The example uses invented research data and scripted model responses. It tests the software; its scores do not show how real models perform.

## Run with models

Install the dependencies and set `OPENAI_API_KEY` in the environment. The writing module reads the key through the OpenAI SDK and does not load a `.env` file.

~~~text
python -m pip install -r requirements.txt
python -m src.writing run --package PACKAGE.json --v0 V0.json --writer-model WRITER --checker-model CHECKER --output runs/pilot-001
~~~

Choose model IDs available to the API account that support structured outputs. Omit `--v0` to generate the initial draft. The checker must use a different model ID from the writer. By default, the critic uses the chosen checker model in a separate call with its own prompt. Use `--critic-model CRITIC` to choose another critic model, also different from the writer. The main method includes critique calls and their additional token allowance. Paid calls are separate from the offline tests.

A separate audit uses an evaluator whose ID differs from every model used during refinement:

~~~text
python -m src.writing audit --run runs/pilot-001 --evaluator-model EVALUATOR --output evaluation-output/audit-001
~~~

Different model IDs do not guarantee independent judgements. Human assessment can check whether the automated decisions are useful and accurate.

## Files

~~~text
data/                         Literature metadata and pilot generated sections
emnlp-literature/              Metadata collector
src/sample_papers.py           Random ten-paper sample with a fixed seed
src/generate_ai_sections.py    Pilot section generation from titles and abstracts
src/writing/                  Drafting, diagnostics, revision, checks and commands
examples/                     Synthetic package and six-section draft
tests/                        Offline tests
docs/                         Input format, evaluation and feature-selection guides
~~~

The existing pilot corpus contains 60 sections generated from ten titles and abstracts. Use it for exploratory style analysis. Its detailed claims have not been checked against full papers.

The pilot generator uses the committed ten-paper sample, labels missing topics `unspecified`, checks input hashes when resuming and writes a new output file. It is separate from package-based drafting. Sampling is random with a fixed seed. Keep the original data and generated corpus intact.

## What has been tested

The offline tests cover input validation, edit scope, rejected changes, checker failures, rollback, stopping rules, token budgets and review exports. Real-package performance, feature calibration, preservation accuracy and human ratings still need evaluation. The literature collector and pilot corpus generator are outside these offline tests.

