# Fact or Form? A Controlled Invariance Audit of Hallucination Detectors

Draft V0 — revised 5 November 2026 after full-text review of all 26 Cluster 0 papers and three close 2026 papers. Proposed study; no experimental results are reported.

## Abstract

Hallucination detectors are intended to respond to factual error or lack of source support, yet their scores may also vary with answer length, lexical overlap and phrasing. Existing research already identifies label misalignment, domain shift, response-length effects and detector-family blind spots. The defensible gap is therefore not another broad robustness benchmark but a paired form-invariance audit that holds factual status and evidence fixed. We propose passage-grounded question answering in two domains. Each item will have one human-validated correct answer and one minimally incorrect answer; each answer will be realized as a concise form, a meaning-preserving lengthened form and a similar-length paraphrase. Representative consistency-, uncertainty-, representation- and supervised detectors will be compared with simple length and overlap baselines. Evaluation will jointly measure correct–incorrect discrimination and within-label score stability using the underlying item as the paired unit. A detector that is stable but indiscriminate, or accurate in aggregate but form-sensitive, will not be treated as successful. The contribution is a controlled diagnostic protocol for separating factual sensitivity from answer-form sensitivity in a bounded short-answer setting.

## 1. Introduction

A hallucination detector should ideally change its judgment when factual support changes and preserve it when only wording changes. Aggregate benchmark accuracy does not reveal whether this happens. A detector can achieve a high score by exploiting answer length, reference overlap, dataset style or label construction. Conversely, a detector that gives every answer the same score is perfectly invariant but useless. Factual discrimination and form invariance must therefore be measured together.

The full-paper review shows that broad claims about unexamined robustness are untenable. Janiak et al. demonstrate that lexical-overlap labels can exaggerate progress and that simple length information can be highly predictive. Their human validation is curated, and their analysis notes that length is associated with outcomes without establishing it as a direct cause. Wu et al. explicitly distinguish response consistency from factual accuracy and identify response length as a limitation. [Janiak et al., 2025, human-validation design, p. 13](https://aclanthology.org/2025.emnlp-main.1761.pdf#page=13); [Janiak et al., length caveat, p. 18](https://aclanthology.org/2025.emnlp-main.1761.pdf#page=18); [Wu et al., 2025, consistency versus accuracy, p. 2](https://aclanthology.org/2025.emnlp-main.1554.pdf#page=2); [Wu et al., limitation, p. 9](https://aclanthology.org/2025.emnlp-main.1554.pdf#page=9).

The 2026 comparison set further covers distribution shift, strict aggregation and consistency–confidence taxonomies. Fortifying Hallucination Detection studies cross-domain transfer but operationally treats incorrect short answers as hallucinations. A large evaluation of hallucination metrics uses strict response aggregation and, in one analysis, optimizes a threshold on the test set. DECK maps different hallucination types to consistency and confidence signals while noting correctness-control caveats. [Fortifying Hallucination Detection, 2026, label definition, p. 3](https://aclanthology.org/2026.findings-emnlp.113.pdf#page=3); [scope limitation, p. 9](https://aclanthology.org/2026.findings-emnlp.113.pdf#page=9); [2026 evaluation study, aggregation, p. 6](https://aclanthology.org/2026.acl-long.680.pdf#page=6); [threshold choice, p. 14](https://aclanthology.org/2026.acl-long.680.pdf#page=14); [DECK, grading design, p. 13](https://aclanthology.org/2026.findings-aacl.164.pdf#page=13).

What remains usefully isolated is a paired intervention on answer form:

1. **RQ1—Discrimination:** Within an item, does a detector rank a supported answer above a minimally incorrect answer?
2. **RQ2—Invariance:** How much does its score vary among meaning-equivalent forms with the same factual label?
3. **RQ3—Relative magnitude:** Is within-label form variation small relative to the correct–incorrect score gap?
4. **RQ4—Shortcuts:** Do simple length, overlap or semantic-similarity baselines explain similar behavior?

The study is limited to passage-grounded short QA. It does not claim to represent every form of hallucination.

## 2. Related Work and Gap Establishment

### 2.1 Detector families already use diverse signals

AGSER uses attention-guided self-reflection and response consistency without task-specific training samples, but its failure analysis includes difficulty with query segmentation. IRIS derives features from truth-verification behavior and internal representations; its reported scope is bounded to single statements. These methods motivate including reflection and representation families rather than assuming that every detector is a surface classifier. [AGSER, 2025, no-training-sample design, p. 11](https://aclanthology.org/2025.emnlp-main.1063.pdf#page=11); [AGSER, segmentation failure, p. 12](https://aclanthology.org/2025.emnlp-main.1063.pdf#page=12); [IRIS, feature design, p. 4](https://aclanthology.org/2025.emnlp-main.1124.pdf#page=4); [IRIS, scope limitation, p. 9](https://aclanthology.org/2025.emnlp-main.1124.pdf#page=9).

Cluster 0 also contains uncertainty, reasoning-process, multilingual and long-form approaches. Their existence blocks any claim that hallucination detection relies on one signal or that multilingual evaluation is absent. This proposal instead compares accessible representatives under the same controlled answer transformations.

### 2.2 Evaluation validity and domain shift are established problems

The Illusion of Progress provides the closest motivation for including answer length and overlap baselines. Wu et al. warn that consistency is not the same as correctness. Fortifying Hallucination Detection evaluates out-of-distribution transfer, so this proposal cannot claim domain shift as its novelty. DECK shows that different detector signals have different blind spots, which motivates family-stratified reporting.

The remaining gap is an explicit **invariance ratio** within human-validated item pairs: score movement caused by form changes compared with score movement caused by a minimal factual change. This differs from ordinary paraphrase augmentation because the design jointly controls evidence, factual label, item identity and approximate length.

### 2.3 Target construct

For this study, a response is **supported** when all material claims needed to answer the question are entailed by the supplied passage. It is **incorrect** when it contains a material contradiction or unsupported answer claim. This is a bounded operational definition. It does not cover fabrication in open-ended dialogue, citation correctness, long-form mixtures of supported and unsupported claims or epistemic uncertainty beyond the passage.

## 3. Methodology

### 3.1 Items and domains

We plan 120 passage–question items from each of two redistributable domains, for 240 underlying items. Candidate domains will differ in style while keeping answers short and evidence explicit. Dataset versions, licensing and sampling rules will be frozen before answer variants are constructed.

Each item receives a reference evidence span. Items requiring external knowledge, multiple defensible answers or unresolved coreference will be removed before detector testing. A 20-item pilot per domain will test the construction and annotation rules; pilot items will not enter the frozen test set if rules change.

### 3.2 Correct and minimally incorrect answers

For every item, annotators will create:

- one concise supported answer; and
- one minimally incorrect answer that changes a single substantive entity, quantity, time, polarity or relation while keeping syntax and length similar.

The incorrect answer must remain fluent and responsive to the question. It cannot be made incorrect merely by adding nonsense or obvious formatting artifacts. The changed element and evidence contradiction will be logged.

### 3.3 Form variants

Each answer then receives three forms:

| Form | Constraint | Purpose |
|---|---|---|
| Concise | Minimal complete answer | Reference form |
| Lengthened | Add discourse or explanation without adding a new factual claim | Test length sensitivity |
| Paraphrased | Preserve meaning at approximately matched length | Test phrasing sensitivity |

This yields six variants per item. Lengthening cannot introduce new factual content. Paraphrases may change syntax and wording but must preserve the answer's supported or incorrect status.

Two annotators independently label every variant against the passage as Supported, Incorrect or Ambiguous/Insufficient Evidence. They also flag added claims, unnatural wording and failed paraphrases. Disagreements are adjudicated by a third reviewer. If any required variant cannot preserve the intended label, all six variants for that item are excluded from the complete paired primary set; counts and reasons remain visible.

### 3.4 Detectors and baselines

Subject to reproducible implementations and licenses, the comparison will include representatives of:

- self-consistency or sampling-based detection;
- uncertainty or likelihood scoring;
- internal-representation or attention-based detection;
- supervised cross-encoder/classifier detection.

Exact versions, prompts, sampling counts and preprocessing will be frozen. Any threshold will be chosen on separate calibration data, never the test set.

Baselines will include response character/token length, lexical overlap with a reference answer or evidence span, semantic similarity to the reference, and a small combination of these features. Baselines are diagnostic: if a complex detector behaves similarly, that does not prove identical internal mechanisms, but it weakens a claim that the score isolates factual support.

## 4. Experiments and Evaluation Plan

### 4.1 Factual discrimination

For each item and form, we will test whether the detector assigns the supported answer a more favorable score than its minimally incorrect counterpart. Primary measures are within-item ranking accuracy and the paired correct–incorrect score difference. AUROC and fixed-threshold class errors will be secondary summaries because they can conceal item-level reversals.

Results will be reported separately by domain, detector family and form. Operational failures and unsupported input lengths remain in coverage tables.

### 4.2 Form invariance

For each underlying answer, within-label form sensitivity will be measured by:

- maximum score range across forms;
- score standard deviation across forms;
- binary decision-flip rate under the frozen threshold;
- rank preservation between supported and incorrect answers across forms.

The main diagnostic compares the absolute within-label form change with the absolute correct–incorrect gap for the same item. A preregistered summary may use:

**form-sensitivity ratio = within-label score range / (absolute supported–incorrect gap + ε)**,

where ε is fixed from calibration-scale considerations rather than chosen after viewing test results. Raw numerator and denominator will always accompany the ratio because ratios can become unstable near a zero factual gap.

### 4.3 Paired analysis and uncertainty

The underlying passage–question item is the resampling unit. Item-cluster bootstrap intervals will retain both labels and all forms together. Domain-level estimates precede any pooled average. Multiple detector comparisons will be treated as descriptive unless a smaller confirmatory set is preregistered.

Lengthened and paraphrased variants will also be compared with their concise sources on length, semantic similarity and reviewer naturalness. If a transformation changes meaning or quality, the item will not be used to attribute score movement to form alone.

### 4.4 Prospective interpretation rules

| Pattern | Interpretation |
|---|---|
| Strong discrimination and low form variation | Desired behavior in this bounded setting |
| Strong aggregate AUROC but frequent within-item reversals | Benchmark performance masks unstable item behavior |
| Low form variation and low discrimination | Invariant but uninformative detector |
| Form variation rivals or exceeds factual gap | Material sensitivity to answer realization |
| Length/overlap baseline matches detector pattern | Surface shortcut is a plausible explanation requiring further study |
| Effect appears in one domain only | Domain-bounded finding, not general robustness |

We will not use a nonsignificant difference to claim equivalence. If invariance is a confirmatory aim, an equivalence margin must be justified before testing.

### 4.5 Limitations

The design covers short passage-grounded answers, not long-form generation with many claims. Meaning-preserving lengthening is difficult and human validation remains imperfect. Minimal factual errors may be easier than natural hallucinations. Some detector families require white-box access or repeated sampling, making comparisons operationally unequal. Calibration data may not transfer across domains, and proprietary model drift may affect reproduction. A controlled form intervention diagnoses sensitivity but does not prove why a model uses a feature internally.

## 5. Conclusion

The literature already documents label problems, length effects, domain shift and detector-family blind spots. The defensible next step is a narrower paired test: hold evidence and factual status fixed, vary answer form, and compare that movement with the score gap created by a minimal factual error. By requiring both discrimination and invariance—and by retaining simple baselines—the proposal avoids mistaking stability, aggregate accuracy or stylistic regularity for factual detection. Experimental results remain to be collected.

## References

- Liu et al. 2025. [Attention-guided Self-reflection for Hallucination Detection](https://aclanthology.org/2025.emnlp-main.1063/).
- Srey et al. 2025. [Unsupervised Hallucination Detection by Inspecting Reasoning Processes](https://aclanthology.org/2025.emnlp-main.1124/).
- Islam et al. 2025. [How Much Do LLMs Hallucinate across Languages?](https://aclanthology.org/2025.emnlp-main.1481/).
- Wu et al. 2025. [Estimating LLM Consistency](https://aclanthology.org/2025.emnlp-main.1554/).
- Janiak et al. 2025. [The Illusion of Progress: Assessing Hallucination Detection Methods](https://aclanthology.org/2025.emnlp-main.1761/).
- 2026. [Fortifying Hallucination Detection Under Distribution Shift](https://aclanthology.org/2026.findings-emnlp.113/).
- 2026. [Large-Scale Evaluation of Hallucination Detection Metrics](https://aclanthology.org/2026.acl-long.680/).
- Chauhan. 2026. [DECK](https://aclanthology.org/2026.findings-aacl.164/).
