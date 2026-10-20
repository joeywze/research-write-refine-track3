# Human Agreement and Repeated-Call Stability in Bilingual LLM Judging

## A controlled, context-grounded QA evaluation proposal

Draft V0 — 20 October 2026. Proposal only: no experimental results. Language, dataset, judge version and reviewer assignments remain subject to Team A approval. This is a narrative draft, not a validated Stage B input file.

## Abstract

We propose a small replication-and-extension study of language-model judging in context-grounded short question answering. The study will compare English with one additional language using matched correct and deliberately incorrect answers. Two fluent human raters will independently assess every response in each language, with disagreements adjudicated before model evaluation. A fixed judge will evaluate the responses in three repeated calls per condition. The primary comparison will hold English judging instructions constant across response languages; a secondary comparison will use meaning-matched target-language instructions. Planned measures distinguish human-reference agreement, cross-language decision changes, abstention and repeated-call stability. The intended contribution is an auditable evaluation protocol and a narrowly scoped assessment of the selected setting, not a claim that multilingual judge evaluation is new. No effect direction or experimental outcome is assumed.

## 1. Introduction

Multilingual judge reliability already has direct empirical precedents. Fu and Liu study parallel multilingual evaluation, while Chung and Freienthal investigate cross-language stability under controlled dialogue generation. These studies establish that neither multilingual consistency nor controlled evaluation is an unexplored topic. [Fu and Liu, 2025](https://aclanthology.org/2025.findings-emnlp.587/); [Chung and Freienthal, 2026](https://aclanthology.org/2026.mme-main.8/).

Our proposed question is narrower: in one feasible bilingual QA setting, does a fixed judge agree with adjudicated human correctness labels similarly across matched language versions, and are its repeated decisions stable? Agreement with humans, agreement across languages and agreement across repeated calls will be measured separately. This distinction is operational: a judge could consistently produce the same wrong decision, so repeated agreement alone would not demonstrate correctness.

The work is framed as replication with candidate extensions. We have not established that its combined protocol is absent from the wider literature. The literature review and planned experiment therefore support an evidence-backed proposal, not a confirmed novelty claim or a completed performance assessment.

## 2. Related Work

Several Cluster 7 findings constrain the proposal. Wang et al. explicitly identify English evaluation as their study's scope and multilingual judging as future work. Yu et al. test English and Chinese judging prompts, but their variants also differ in instruction detail. Wu et al. include translation evaluation across six target languages. These are different designs, not interchangeable evidence of a single missing capability. [Wang et al., 2025, limitations](https://aclanthology.org/2025.emnlp-main.103.pdf#page=10); [Yu et al., 2025, §4.3.3](https://aclanthology.org/2025.emnlp-main.712.pdf#page=7); [Wu et al., 2025, §4.2](https://aclanthology.org/2025.emnlp-main.1307.pdf#page=5).

The closest QA counterexample is PolyJudge-Uncertain, which already combines multilingual factual answers with correct/incorrect variants. Its limitations identify incomplete human validation of the final rerun. M-RewardBench also includes native-speaker preference validation, showing that multilingual human-reference evaluation is not generally absent. [Datta and Baitalik, 2026, §3.2](https://aclanthology.org/2026.acl-srw.33.pdf#page=3) and [limitations](https://aclanthology.org/2026.acl-srw.33.pdf#page=8); [Gureja et al., 2025, §6.3](https://aclanthology.org/2025.acl-long.3.pdf#page=8).

Our intended distinction is a context-supported correctness task with human labels in both selected languages, coupled with explicit repeat-call and instruction-language comparisons. This is a proposed protocol difference, not proof of novelty. The accompanying evidence review retains counterevidence and unresolved search leads rather than treating the 18-paper sample as the entire field.

## 3. Methodology

### 3.1 Task and matched data

The proposed feasibility pilot will contain 20 underlying passage/question items, each paired with a correct answer and a minimally changed incorrect answer. Each item will be realized in English and one additional language, producing 80 response texts before exclusions. We will choose the target language according to fluent-reviewer availability, translation feasibility and permissible data use. We will not infer a high-/low-resource distinction from this two-language selection.

Data provenance and licences will be recorded before reuse. A bilingual reviewer will check that translations preserve the passage meaning, question answerability and intended answer error. The incorrect variant must remain genuinely wrong, rather than a synonym or acceptable paraphrase. Practice items used to clarify the rubric will be separate from the analysis sample. The texts and exclusion rules will be frozen before judge outcomes are examined.

### 3.2 Human reference and shared rubric

Two raters fluent in the response language will independently label each response as Correct, Incorrect or Insufficient evidence. Correct requires an answer supported by the passage without a material unsupported claim. Incorrect covers a material contradiction, unsupported answer content or failure to answer the question. Insufficient evidence records ambiguity or inadequate information. Meaning-preserving paraphrases are acceptable; style is not a scoring dimension.

Raters will be blinded to model outputs and intended answer condition. Raw labels, reasons and pre-adjudication agreement will be retained. Disagreements will be adjudicated from the passage, using a third fluent reviewer if necessary. Unresolved underlying items and all their paired variants will be excluded from the primary paired analysis, with reasons reported. An automated fact checker will not substitute for the human reference. Reviewer overlap between languages will be documented.

### 3.3 Judge conditions

The minimum design uses one fixed judge, J1. Its exact model/version and supported inference settings remain unresolved and must be frozen before execution. A second model family, J2, is an optional replication condition subject to access and budget; it is not part of a completed experiment.

English responses and target-language responses will first be judged using the same English rubric and output-label format. The target-language responses will additionally be judged using a bilingual-reviewed translation of that rubric. Context, question and answer will remain in the response language, so the primary contrast varies all three together rather than isolating answer language alone. The secondary contrast changes instructions while holding target-language content fixed; it does not constitute a complete factorial design.

Each response/condition will receive three calls with identical recorded settings. Calls will be made in separate contexts, without previous verdicts. Prompts, outputs, model identifiers, dates, parsing rules, supported sampling controls and failures will be retained. Assuming all 20 items qualify, J1 requires 360 scheduled calls. J2 would add another 360. Human annotation requires 160 initial ratings, excluding equivalence review, practice and adjudication.

## 4. Experiments: Evaluation Plan

The primary outcome will be unconditional agreement with the adjudicated binary human reference. For each response, we will average agreement indicators across its scheduled repeats, then aggregate by language and instruction condition. Judge abstentions, invalid outputs and failed scheduled calls will be non-matches in this measure and reported separately. Conditional binary agreement and Cohen's kappa will be accompanied by decision coverage, preventing selective non-decisions from being hidden.

We will also report acceptance of human-incorrect answers and rejection of human-correct answers, with separate abstention/failure rates. Repeated-call stability will be the fraction of response/condition cells with three identical valid labels; repeated abstentions will be distinguished from repeated substantive decisions. Cross-language decision changes will be calculated only when both paired binary decisions exist, with paired coverage and non-decision mismatches reported. Human agreement before adjudication will be described separately from judge agreement against the adjudicated reference.

Comparisons will preserve the matched underlying item structure. Exploratory 95% bootstrap intervals will resample whole items, keeping their translations, answer variants and repeat calls together. Repeats will not be counted as independent items. The 20-item design is a feasibility pilot, not a powered confirmatory study; wide or degenerate intervals and undefined kappa values will be reported transparently. A non-significant contrast will not establish equivalence.

No results are available. The planned analysis will allow several outcomes, including similar language performance, systematic decision differences, stable errors or failures attributable to item construction. None is assumed in advance. Conclusions will be restricted to the chosen task, language pair, judge configuration and sample.

## 5. Conclusion

This proposal develops a source-traceable bilingual QA evaluation with human reference labels, controlled instruction contrasts and repeated-call diagnostics. Its value is an auditable replication-and-extension plan, not a claim to introduce multilingual judging. Before execution or final handover, Team A must approve the language and reviewer access, item source, judge configuration, budget and remaining closest-work comparisons. No claims about improved judge performance, statistically established language effects or general multilingual reliability can be made without the proposed evidence.

## References

- Isaac Chung and Linda Freienthal. 2026. [Cross-Lingual Stability of LLM Judges Under Controlled Generation: Evidence from Finno-Ugric Languages](https://aclanthology.org/2026.mme-main.8/). MME, 133–148.
- Rajashik Datta and Sanjan Baitalik. 2026. [Confidence as a Tie-Breaker: Reassessing Multilingual Hedging Bias in LLM-as-a-Judge Evaluation](https://aclanthology.org/2026.acl-srw.33/). ACL Student Research Workshop, 393–402.
- Xiyan Fu and Wei Liu. 2025. [How Reliable is Multilingual LLM-as-a-Judge?](https://aclanthology.org/2025.findings-emnlp.587/). Findings of EMNLP, 11040–11053.
- Srishti Gureja et al. 2025. [M-RewardBench: Evaluating Reward Models in Multilingual Settings](https://aclanthology.org/2025.acl-long.3/). ACL, 43–58.
- Peifeng Wang, Austin Xu, Yilun Zhou, Caiming Xiong and Shafiq Joty. 2025. [Direct Judgement Preference Optimization](https://aclanthology.org/2025.emnlp-main.103/). EMNLP, 1979–2009.
- Ling-I Wu, Weijie Wu, Minyu Chen, Jianxin Xue and Guoqiang Li. 2025. [Co-Eval: Augmenting LLM-based Evaluation with Machine Metrics](https://aclanthology.org/2025.emnlp-main.1307/). EMNLP, 25754–25776.
- Jiachen Yu, Shaoning Sun, Xiaohui Hu, Jiaxu Yan, Kaidong Yu and Xuelong Li. 2025. [Improve LLM-as-a-Judge Ability as a General Ability](https://aclanthology.org/2025.emnlp-main.712/). EMNLP, 14099–14115.
