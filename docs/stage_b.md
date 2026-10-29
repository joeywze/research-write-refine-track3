# Stage B writing guide

## 1. Inputs and responsibilities

Team A reviews the literature, assesses the research gap and approves the Research Package. Stage B uses that package to produce or revise a six-section draft. The package format is version `0.1`; changes to the hand-off must retain the approved question and evidence.

The writing workflow runs automatically once its inputs, configuration and model credentials are supplied. Human assessment helps evaluate the outputs and establish benchmark labels. It is not required to approve individual revisions.

See [the synthetic package](../examples/research_package.json) for the current format.

| Field | Contents |
| --- | --- |
| schema_version, package_id | Format version and package ID |
| title, research_question | Approved research focus |
| gap, contribution | Supported gap and proposed contribution |
| methodology, study_status | Approved design; proposed or completed |
| sources | Source IDs, titles and retrievable identifiers |
| evidence | Excerpts, source IDs and locations in the source |
| claims | Claim text, type, evidence links and qualifications |
| technical_terms | Terms to retain during revision |
| limitations, unknowns | Qualifications and missing information |

Claims about sources and completed results need evidence. Proposals may describe planned work, but must not present it as a completed finding. Claim IDs link to evidence IDs, which link to sources.

Format validation checks these links. It cannot verify the accuracy of an excerpt or establish that the research gap is sound.

## 2. Initial draft and paragraph mapping

V0 may be supplied or generated. It must include `schema_version`, `package_id` and an ordered list of paragraphs. Each paragraph has a unique `paragraph_id`, a section name, text and known `claim_ids`.

All six sections and all package claims must appear. Claims supported by a source need its citation token, such as `[[S1]]`, in the same paragraph. The Markdown export lists the cited source titles and links.

A separate model checks V0 against the package before revision starts. If that check fails or is unavailable, the run stops. Generated responses are saved before format validation so invalid output can be inspected.

Paragraph IDs, order, sections and claim mappings stay fixed during revision. The checker also reads the prose: assigning a claim ID does not prove that the paragraph expresses it correctly.

## 3. Diagnostics and scoring

The default rules flag:

- Sentences longer than 35 words.
- Two or more occurrences from a fixed transition list in an eligible paragraph.
- Very similar sentence lengths, assessed only with at least four sentences.

Paragraphs below 20 words are ineligible. If every paragraph is ineligible, the score is null. Sentence splitting is approximate and can misread abbreviations or mathematical prose.

The score counts flagged issues; lower is better. These rules are still being developed. A useful transition or necessary qualification should stay even if it raises a count.

Additional measurements are saved for analysis but do not affect scores or edit targets. The main method combines **Rule-based checks** and **LLM writing review**. The latter identifies passages that could benefit from clearer, more precise, better-connected or more natural wording, using six detailed criteria.

Reports label the counts **Review points flagged by rules** and **Review points flagged by the LLM**. A review point deserves consideration but is not necessarily a defect or an accepted edit. The LLM count includes actionable paragraph-criterion findings, so it can exceed six across a paper. Both methods may flag the same passage; their counts are not added into one score. See [feature selection](feature_selection.md) for calibration and candidate rules.

## 4. Revision and stopping

The generic and guided versions start from the same V0 and initially edit the same paragraphs. Both receive the package and draft; only the guided writer receives diagnostics. They use the same writer model and per-call output limit, with equal token allowances for writing and preservation checks.

The generic version makes one attempt and accepts a candidate if its content is preserved. Its acceptance does not depend on style scores. The guided version allows up to three attempts. The default live method is `rules-critic`. Use `--method rules-only` for the comparison method, which accepts a preserved candidate only if the rule count falls by the configured minimum, usually one flag. The offline scripted demonstration still tests this rules-only path.

In the main method, a preserved guided candidate receives a fresh critique. Neither issue count may rise, and at least one must fall by the minimum. New research problems, an issue becoming unassessable, or a paragraph becoming too short to score cannot count as improvement.

The run stops at the attempt limit, when no targets remain, or after an unchanged candidate, insufficient improvement, failed preservation, unavailable check, exhausted budget, invalid response or model error. A failed attempt counts towards the limit.

Each accepted draft is saved before the next attempt. A rejected candidate leaves the last accepted draft intact. The SDK makes no automatic retries. Interrupted runs retain their saved files; automatic resumption is not implemented.

## 5. Content checks

Deterministic checks compare paragraph IDs, order, claim mappings, citation counts, numbers, mathematical expressions and protected terms. For V0, they reject numbers absent from the package evidence or approved content and check that protected terms appear.

The model checker receives the package, candidate, V0 and last accepted draft. It receives no style scores or critic feedback. It checks every paragraph and claim, including scope, causality, uncertainty, attribution, methodology, gap, contribution, limitations and study status.

Results are PASS, MAJOR_DRIFT, UNSUPPORTED_ADDITION, CITATION_MISMATCH or CHECK_ERROR. An incomplete or unavailable check prevents acceptance.

These checks can make mistakes. Unchanged citation tokens may still be attached to the wrong claim. A numerical value can retain its digits but change meaning. Strict checks may also reject harmless changes, such as equivalent equation formatting. Assess checker accuracy with labelled examples before relying on its decisions.

## 6. Comparing outputs

Use V1 for the final accepted generic draft and V2 for the final accepted guided draft. V2 versus V1 is the comparison of the complete workflow, including extra calls and checking. Also compare each with V0.

The first generic and guided attempts provide a narrower comparison of feedback when the initial paragraph targets are shared. They do not measure the benefit of selecting paragraphs or of unrestricted rewriting. Report subsequent iterations and their cost separately.

Keep failed cases and rejected attempts in the results. Compare versions within the same paper and keep all sections and variants of that paper in one data partition. Freeze prompts, rules and model settings before evaluating held-out cases. Human ratings must not be used to select which iteration becomes V2.

## 7. Optional independent assessment

The review export creates:

- `raters/`: anonymised texts, source evidence, a rating template and instructions.
- `private/`: the condition key, run information and analysis plan.

Identical drafts appear once, with their conditions recorded in the private key. Parseable rejected candidates are included. Invalid outputs remain recorded as failures. Use one run per package.

For writing assessment, distribute the candidate texts without the condition key, diagnostic scores or preservation evidence. Collect and lock those ratings before releasing V0 and source evidence for the preservation assessment. Alternatively, use separate reviewer groups. The exporter creates both sets of files; staged distribution is the study organiser's responsibility.

Rate clarity, coherence, naturalness and technical precision. Naturalness concerns fluent academic prose. Reviewers should record uncertainty when they cannot assess an item. Before the study, agree criterion-specific examples and practise on cases outside the evaluation set. Where feasible, collect independent ratings from at least two reviewers and report their disagreement.

The `audit` command runs a separate preservation evaluator. Its model ID must differ from the writer, checker and critic. It receives no style scores or acceptance decisions. Scripted examples cannot be used for this model evaluation.

Report rating differences within paper, preservation failures, failed attempts, token usage and latency. Keep assessment cases separate from diagnostic development. Human-labelled challenge cases and a completed human-rating study are not included in the current example.

## 8. Saved runs and budgets

Use a new directory for every run. It stores the package, settings, hashes, V0, candidates, checks, diagnostics, accepted drafts, attempt records and events. Logs include prompt and schema hashes, model and response IDs, usage where available, and timing. Research text may appear in the local logs.

The OpenAI SDK reads `OPENAI_API_KEY` from the environment. Keep it outside packages and drafts. The writing module does not load a `.env` file. Its [structured-output interface](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) rejects incomplete or unusable responses. See the [SDK guide](https://developers.openai.com/api/docs/libraries) for authentication.

The default token allowance is 200,000 for V0 and separately for each revision version. The main method has one additional allowance shared by the critic's initial and candidate assessments. Critic calls appear under `critique` in the cost summary. The rules-only comparison omits those calls.

Before each call, the adapter reserves UTF-8 input bytes plus the output limit and an overhead allowance. Reported usage replaces that estimate; unknown usage retains it. This is a local spending control, not an exact token count or a billing guarantee. Missing usage is reported as unknown.

Offline tests use scripted responses. Live API behaviour, writing quality and preservation accuracy on real packages require separate evaluation.
