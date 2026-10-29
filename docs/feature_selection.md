# Choosing writing diagnostics

Team A supplies the approved research question and evidence. Diagnostics help improve how that material is written. If an argument needs new evidence or a different design, the critic records the problem for review rather than asking the writer to invent a solution.

## Current features

The main method combines the original three rules with the LLM critic. The rules-only method remains available for comparison. The extra measurements below are saved for analysis and do not trigger edits or change scores.

| Feature | Current treatment |
| --- | --- |
| Sentence-length variance | Population variance from two sentences; coefficient of variation (CV) from four. Check sentence boundaries and differences between sections. |
| Hedge density | Counts from an English phrase list and occurrences per 100 words. Necessary qualifications should stay. |
| Repeated n-grams | Repeated trigrams within sentences and their excess occurrences. Repetition of a technical term may be useful. |
| Adjective density | Deferred until a suitable part-of-speech tagger has been tested. Word endings alone would give unreliable counts. |
| Paragraph-length regularity | Word-count CV within a section, requiring at least three paragraphs. |
| Repeated transitions | Phrase counts and the existing provisional flag. Review whether each transition helps the argument. |

LLM writing review identifies passages that could benefit from clearer, more precise, better-connected or more natural wording. Internally, the critic assesses six criteria for each paragraph: specificity, argument strength, formulaic language, inappropriate hedging, generic transitions and unnatural symmetry.

An ACTIONABLE finding needs a quote from the paragraph, an explanation and a suggested wording change. NO_ISSUE, INSUFFICIENT_EVIDENCE and NEEDS_RESEARCH do not instruct edits. Missing paragraphs or criteria, invented quotes and malformed responses cause an error. A correctly formatted response can still contain poor advice.

## Deciding what to keep

1. Allocate cases before tuning. Keep every section and revision of one paper together in either development or evaluation.
2. Use verified packages and comparable academic sections. Match field, section and approximate length. The old title-and-abstract corpus alone cannot test grounding or preservation.
3. Review a spread of high and low feature values, including passages where the feature is likely to be misleading. Ask reviewers to mark flags as useful, appropriate/harmless, misleading or uncertain, with a reason and possible safe edit.
4. Check how many reviewed flags are useful. Review an additional sample of unflagged passages to find missed problems. Record reviewer disagreement, section differences, repeated-critic consistency and cost.
5. Run otherwise comparable refinement with and without a feature. Compare independent writing ratings and preservation outcomes within paper, including failed attempts.
6. Keep, defer or drop the feature. Record the examples, counts, uncertainty, thresholds, applicable sections and versions used. Prefer a smaller set when features duplicate each other or add little benefit.
7. Record the final code commit, prompts, model IDs, settings, stopping rules and data allocation. Use untouched cases for the reported evaluation. Further tuning starts another development cycle.

Choose acceptable error rates before examining evaluation results. A lower internal issue count alone is not evidence that readers prefer the text.

The extra measurements and critic have not yet been calibrated against reviewed real cases. The synthetic examples test software behaviour only.

## Should more rules trigger revision?

Test further candidates before adding automatic triggers. Start with repeated phrases and sentence openings: they may reveal redundancy, but repeated technical language can be necessary. Let the critic judge whether a specific passage needs a wording change. Hedge counts and paragraph regularity need the same contextual judgement. The current three rules also need calibration; they were chosen as a simple baseline, not because a study proved them superior.

Enable a new rule only when reviewed development cases show useful, safe edits and an otherwise comparable run gains something from including it. The LLM rubric already covers redundant wording, unnecessary hedging and weak transitions, so additional rules should add evidence or consistency rather than duplicate its findings.

## Measure without model calls

~~~text
python -m src.writing measure --package examples/research_package.json --v0 examples/v0.json --output runs/feature-review-001
~~~

This saves `diagnostics.json` in a new directory. It needs no API credentials or network connection.

## Main method and comparison

~~~text
python -m src.writing run --package PACKAGE.json --v0 V0.json --writer-model WRITER --checker-model CHECKER --critic-model CRITIC --output runs/critic-pilot-001
~~~

The live command defaults to `--method rules-critic`. If `--critic-model` is omitted, it uses the chosen checker model for a separate critique call with its own prompt. A named critic must also differ from the writer. A later evaluator must differ from every model used during refinement.

Use `--method rules-only` for the comparison method. Do not supply `--critic-model` with that option. The offline demo and direct library calls without a critic retain the rules-only path.

Saved reports label the counts **Review points flagged by rules** and **Review points flagged by the LLM**, under the methods **Rule-based checks** and **LLM writing review**. A review point may or may not lead to a safe edit. The counts are not marks out of 100 and may overlap, so they remain separate. Existing data keys and CSV headers are retained for compatibility; the report includes their readable labels and the selected method.

The critic first assesses the accepted V0. Both rewrite versions receive the same initial paragraph targets, but only the guided writer receives the feedback. The generic candidate is accepted on preservation alone.

For guided candidates, preservation is checked before the critic reassesses the text. Acceptance requires neither issue count to rise and at least one to fall by the configured minimum, usually one. A new NEEDS_RESEARCH finding, an actionable issue becoming unassessable, or loss of surface-score eligibility prevents acceptance. This rule may reject a useful edit when the critic is inconsistent; its accuracy still needs evaluation.

Responses, findings and failures are saved. A candidate critique error stops guided revision and keeps the last accepted draft. If the initial critique fails, neither rewrite starts. The run does not silently switch methods or retry revisions.

The critic has one additional token allowance shared by its initial and candidate assessments. Calls are recorded under `critique` in `cost_summary.json`, with individual usage and timing in `events.jsonl`. Include that cost when comparing the final guided and generic drafts.

## Independent assessment

Once configured, the workflow runs without human approval of its revisions. Human assessment is used to check writing quality, calibrate diagnostics and label preservation examples.

Use the final accepted guided draft (V2) versus the final generic draft (V1) for the complete-workflow comparison, and report its extra computation. First attempts provide a separate comparison of feedback on the shared paragraph targets. Select V2 using the run's acceptance and stopping rules, before inspecting evaluation ratings.

Real packages, reviewer labels, a preservation challenge set and completed quality results still need to be collected. See [the writing guide](stage_b.md) for assessment files and responsibilities.

API details are described in the [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses). The [evaluation guide](https://developers.openai.com/api/docs/guides/evaluation-best-practices) discusses task-specific tests and human calibration.
