# Human–Judge Agreement and Decision Stability in Bilingual Question Answering: A Controlled Evaluation Proposal

## Abstract

Agreement with human judgments, consistency across languages and stability across repeated calls describe different aspects of an automated evaluator. A judge may produce stable decisions that are nevertheless incorrect, or agree with humans in one language but not on a meaning-matched version in another. We propose a controlled bilingual study that measures these properties separately in context-grounded short question answering. A feasibility pilot will contain 20 passage–question items, each with a correct and a deliberately incorrect answer in English and one additional language. Two fluent raters will independently assess each response before adjudication. One fixed language-model judge will evaluate the responses under English instructions, with an additional target-language instruction condition and three calls per condition. The analysis will separate human-reference agreement, cross-language decision changes, repeated-call stability and non-decisions. The proposed contribution is a human-validated replication-and-extension protocol for a bounded QA setting, rather than a claim to introduce multilingual judging. The study is designed to distinguish incorrect judgments from unstable judgments and data-construction problems; no direction of effect is assumed.

## Introduction

When a language model is used to evaluate answers, the evaluator itself becomes an object of assessment. Multilingual studies already examine language-dependent evaluation: Fu and Liu evaluate judgments on parallel language versions, while Chung and Freienthal investigate cross-language stability in controlled customer-support dialogues. Their work provides direct precedents for studying language-dependent evaluation, rather than a basis for claiming that multilingual judging has been overlooked. [[S01]]; [[S02]].

For a particular judge and task, however, three questions remain distinct. Does the judge agree with a human reference? Does it preserve its decision when equivalent content is presented in another language? Does it repeat its own decision under the same settings? None logically guarantees the others. A judge that always accepts an incorrect answer is stable but wrong. A disagreement between language versions could reflect judge behavior, an imperfect translation or an ambiguous reference label. Our study therefore combines human assessment of the test material with separate measurements of agreement and stability.

We focus on short answers evaluated against a supplied passage. This bounded task allows answer correctness to be checked against explicit evidence rather than an unrestricted judgment of writing quality. The proposed pilot addresses three research questions:

1. **RQ1—Human agreement:** Under the same English judging instructions, how does agreement with adjudicated human correctness labels differ between English and a second language on matched QA content?
2. **RQ2—Decision stability:** How often do judgments differ across matched language versions, and how often does a judge repeat its decision across calls with fixed settings?
3. **RQ3—Instruction sensitivity:** For target-language content, does using meaning-matched target-language instructions change agreement or stability relative to English instructions?

The intended contribution is a transparent replication-and-extension protocol with human reference labels in both selected languages, explicit language controls and separate error and stability measures. Its value does not depend on finding a language disadvantage: similar agreement, stable errors or problems in the test material would require different interpretations. The novelty of the combined protocol remains unconfirmed pending a broader literature comparison.

## Related Work

An English-focused study can motivate extending that study without establishing an absence elsewhere. For example, Wang et al. explicitly limit their evaluation to English and identify multilingual judging as future work. Conversely, Wu et al. examine translation evaluation across six target languages. The relevant comparison is therefore between specific tasks and evaluation protocols, rather than English-only and multilingual research as mutually exclusive categories. [[S03]]; [[S04]].

Judging-instruction language also needs to be distinguished from the language of the evaluated content. Yu et al. compare an official English prompt with basic and instructional Chinese prompts, which vary in detail as well as language. Chung and Freienthal include an Estonian instruction-language sensitivity check. Our secondary condition follows this existing work on instruction-language effects but aims to preserve rubric meaning while changing instruction language. [[S05]]; [[S06]].

The following studies directly constrain the proposed contribution. The final column describes our intended comparison, not a claim that its components are unprecedented.

| Study | Relevant verified design feature | Relationship to this proposal |
|---|---|---|
| Fu and Liu (2025) | Ground-truth answers used as evaluation candidates in parallel multilingual tests. [[S01]]. | Include both correct and deliberately incorrect candidates in the proposed QA test. |
| Chung and Freienthal (2026) | Controlled dialogue evaluation; human calibration restricted to Estonian. [[S07]]. | Use a different, passage-grounded task with human reference labels in each selected language. |
| Datta and Baitalik (2026) | Multilingual factual QA already includes correct/incorrect variants; completed human validation remains a limitation of the final rerun. [[S08]], [[S09]]. | Treat mixed-quality multilingual QA as an existing design and emphasize human validation in the proposed extension. |
| Gureja et al. (2025) | Multilingual preference evaluation includes sampled native-speaker validation. [[S10]]. | Distinguish preference agreement from the proposed passage-supported correctness labels. |

These precedents support a narrowly scoped study, not the assertion that multilingual human-reference evaluation is missing. We propose to examine the selected QA setting through an integrated protocol that makes human agreement, language-related decision changes and repeated-call behavior independently observable.

## Methodology

The task is pointwise evaluation: given a passage, a question and one candidate answer, the judge determines whether the answer is supported by the passage. It does not rate fluency, persuasiveness or overall response quality. This restriction makes the object of evaluation explicit and avoids interpreting a factual-correctness label as a general quality score.

The study will compare English with a second language, denoted L. Selection of L will require access to two fluent raters, bilingual equivalence review and suitable reusable material. The language and item source have not yet been selected. They will be fixed before test construction and documented with data provenance and licensing. Language selection is feasibility-driven; the study is not designed to estimate a general effect of language-resource availability.

The planned pilot contains 20 underlying passage–question items. Each item will have a correct answer and a minimally altered incorrect answer in both languages, yielding 80 response texts before exclusions. Incorrect variants will change a substantive entity, quantity or relation while keeping the answer form as similar as practical. Human review will verify that a variant is actually incorrect rather than an alternative valid expression.

The following **synthetic illustration** explains the construction; it is not a sampled item or experimental evidence:

| Component | Illustrative English text |
|---|---|
| Passage | The community library opens at 9 a.m. on Saturdays. |
| Question | What time does the library open on Saturdays? |
| Correct candidate | It opens at 9 a.m. |
| Incorrect candidate | It opens at 10 a.m. |

For a paired language version, the passage, question and both candidates would be translated together. Bilingual review would check preservation of the opening time and the deliberately altered time. Naturally worded translations are required; literal similarity alone will not qualify an item as equivalent.

Practice items will be used to clarify instructions and will remain outside the analysis sample. The reviewed test texts and exclusion rules will be frozen before judge outcomes are examined. Any later discovery of an item defect will be logged rather than silently repaired to change a result.

Humans and judges will use the same three task definitions:

| Label | Decision rule |
|---|---|
| Correct | The answer addresses the question, is supported by the passage and contains no material contradiction or unsupported addition. Meaning-preserving paraphrases are acceptable. |
| Incorrect | The answer makes a material contradicted or unsupported claim, or fails to provide the requested answer. External knowledge does not override the supplied passage. |
| Insufficient evidence | Ambiguity, missing information or unreadability prevents a defensible correctness decision. A reason must be recorded. |

Two raters fluent in the response language will assess each text independently, blinded to the intended condition and all model outputs. Presentation order will be randomized, with paired variants separated where practical. Raw labels and reasons will be retained. Disagreements will be adjudicated against the passage, with a third fluent reviewer if required. Human reference labels will not be replaced by the output of another language model.

Unresolved underlying items will be removed, together with all their answer and language variants, from the primary paired analysis. Counts and reasons will be reported. The same two bilingual people may serve both languages if necessary, but any reviewer overlap will be documented. Agreement before adjudication will describe the initial labeling process, not be substituted for agreement against the final reference.

The minimum study uses one fixed judge, J1. Selection will require support for both languages, accessible inference and recordable settings. Its exact model version and configuration remain to be selected and frozen before collection. An optional second judge from another model family would repeat the protocol as a separate robustness check; the one-judge pilot will not support claims across judge families.

| Condition | Passage, question and answer | Judging instructions | Purpose |
|---|---|---|---|
| A | English | English | Reference condition |
| B | Language L | English | Primary matched language contrast: B versus A |
| C | Language L | Language L | Instruction sensitivity: C versus B |

Conditions A and B change the language of the complete QA material, not answer language alone. Conditions B and C hold that material fixed while changing instruction language. The translated instructions will preserve rubric meaning and use the same output-label codes. This three-condition design does not estimate every possible content-language × instruction-language interaction.

Each response/condition will receive three calls in separate contexts without previous verdicts. The model configuration and prompt template will be fixed within a condition. Full prompts, raw outputs, versions, dates, supported sampling controls, token limits, parsing decisions and technical failures will be recorded. Fixing settings defines the repeatability test; it does not guarantee deterministic outputs.

## Experiments

With 20 qualifying items, there will be 40 candidate responses per content language. Each of the three conditions requires 40 responses × 3 calls, giving 360 scheduled J1 calls. Initial human annotation requires 80 response texts × 2 ratings, or 160 ratings. Translation review, practice, adjudication and any technical retries add workload. An optional J2 would require another 360 calls.

Twenty items and three calls are planning choices for a feasibility pilot, not statistically derived requirements. They allow the proposed workflow and measures to be examined with a bounded annotation and inference workload. Three calls provide only a coarse stability check. A confirmatory design would require a separate sample-size justification based on a specified effect and variability estimate.

The underlying passage–question item is the paired comparison unit. Translations, answer variants and repeated calls derived from that item will not be treated as independent observations.

The primary measure for RQ1 will be **unconditional operational agreement**: the proportion of scheduled calls that produce the adjudicated Correct/Incorrect reference label. Agreement indicators will first be averaged across calls for each response and then across responses within a condition. Abstentions, invalid outputs and technical failures count as non-matches in this operational measure; they are not all interpreted as factual reasoning errors.

To separate these mechanisms, we will also report binary decision coverage, agreement conditional on a valid binary decision, and rates of abstention, invalid output and technical failure. Conditional Cohen's kappa will be reported beside coverage; it will be marked undefined when its denominator is zero. The primary paired contrast is agreement in B minus agreement in A. A contrast caused by technical failures will be described as an operational difference, not automatically a language-understanding deficit.

Error analysis will distinguish accepting a human-incorrect answer from rejecting a human-correct answer. For each type, the denominator is all scheduled calls on responses with the corresponding reference label. Non-decision rates will be shown alongside these error rates. Human raw agreement and kappa before adjudication will be reported separately for each language.

For RQ2, repeated-call stability will be the proportion of response/condition cells with three identical valid labels. Three repeated abstentions will be distinguished from three repeated Correct/Incorrect decisions. A missing or invalid output will not qualify as a stable cell. Agreement with the human reference will be examined alongside stability so that consistently wrong judgments remain visible.

Cross-language decision changes will be assessed between conditions A and B for the same item, answer variant and repeat index. The change rate will be calculated where both outputs are binary decisions, with paired coverage and non-decision mismatches reported. Repeat-index matching defines this pilot's descriptive comparison; it does not make the two calls shared random draws or independent item samples. For RQ3, the same agreement and stability measures will compare C with B.

Exploratory 95% bootstrap intervals will resample whole underlying items, retaining their translations, answer variants and repeated calls together. With a small sample, intervals may be wide or degenerate; such outcomes and undefined statistics will be reported rather than replaced by favorable summaries. A non-significant contrast will not establish cross-language equivalence.

The analysis permits several interpretations. Stable decisions with poor human agreement would indicate consistent error in the tested setting. Decision changes with acceptable translation review would motivate closer examination of language-dependent judging. Translation or reference-label defects would instead require qualification of the evaluation material. These are prospective interpretation rules, not observed findings.

The design is limited to one selected language pair, one primary judge, a small sample and constructed short-answer errors. It cannot establish broad multilingual fairness, deployment safety or performance across model families. Minimal errors may be too easy or unrepresentative of naturally generated answers, creating ceiling effects that this pilot would need to identify.

Human adjudication is a reference procedure, not infallible ground truth. Translation artifacts, reviewer overlap, familiarity with paired variants and exclusion of unresolved items may affect the sample and its labels. Exclusion counts and reasons will therefore accompany the results. Model drift and prior exposure to reused material are additional threats. Reusable public or original non-sensitive passages will be preferred, and provenance and licensing will be recorded before data collection.

## Conclusion

We propose a controlled bilingual QA study that evaluates human–judge agreement, cross-language decision changes and repeated-call stability as distinct outcomes. Matched correct and incorrect candidates, human review in each language and a separate instruction-language contrast make the intended comparisons explicit. The contribution is a bounded, auditable replication-and-extension design. The evaluation plan does not presume a language disadvantage or an improvement from translated instructions; its purpose is to determine which conclusions the selected data and protocol can support. Experimental performance remains to be measured.

## References

[[S01]] How Reliable is Multilingual LLM-as-a-Judge?. https://aclanthology.org/2025.findings-emnlp.587.pdf#page=3
[[S02]] Cross-Lingual Stability of LLM Judges Under Controlled Generation: Evidence from Finno-Ugric Languages. https://aclanthology.org/2026.mme-main.8/
[[S03]] Direct Judgement Preference Optimization. https://aclanthology.org/2025.emnlp-main.103.pdf#page=10
[[S04]] Co-Eval: Augmenting LLM-based Evaluation with Machine Metrics. https://aclanthology.org/2025.emnlp-main.1307.pdf#page=5
[[S05]] Improve LLM-as-a-Judge Ability as a General Ability. https://aclanthology.org/2025.emnlp-main.712.pdf#page=7
[[S06]] Cross-Lingual Stability of LLM Judges Under Controlled Generation: Evidence from Finno-Ugric Languages. https://aclanthology.org/2026.mme-main.8.pdf#page=4
[[S07]] Cross-Lingual Stability of LLM Judges Under Controlled Generation: Evidence from Finno-Ugric Languages. https://aclanthology.org/2026.mme-main.8.pdf#page=5
[[S08]] Confidence as a Tie-Breaker: Reassessing Multilingual Hedging Bias in LLM-as-a-Judge Evaluation. https://aclanthology.org/2026.acl-srw.33.pdf#page=3
[[S09]] Confidence as a Tie-Breaker: Reassessing Multilingual Hedging Bias in LLM-as-a-Judge Evaluation. https://aclanthology.org/2026.acl-srw.33.pdf#page=8
[[S10]] M-RewardBench: Evaluating Reward Models in Multilingual Settings. https://aclanthology.org/2025.acl-long.3.pdf#page=8
