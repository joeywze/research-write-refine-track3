# Do Faithfulness Gains Survive the Metric? A Specificity-Controlled Audit of Iterative Explanation Refinement

Draft V0 — revised 5 November 2026 after full-text review of all 17 Cluster 6 papers and 3 close 2026 papers. Proposed study; no experimental results are reported.

## Abstract

Iterative critique can improve the score used to refine a model explanation, but that improvement need not transfer to another operationalization of faithfulness. It may instead reflect metric-specific optimization, ordinary re-prompting instability, or sensitivity to any added text. Existing work already introduces self-refinement, intervention-guided optimization, prediction–explanation consistency metrics and causal tests of faithfulness measures. The defensible gap is therefore narrower: whether refinement gains survive a held-out metric and exceed specificity controls. We propose a paired audit on natural-language inference and fact verification using two model families. For each initially correct prediction, we will compare the original explanation with self-critique, metric-guided critique, external critique and a neutral rewrite at one and three rounds. The refinement metric will be separated from held-out intervention and consistency measures. Content-free filler, unrelated-text and answer re-injection controls will estimate nonspecific answer-change floors. Prediction accuracy, valid-output coverage, explanation length and blinded human ratings of clarity—not faithfulness—will remain separate outcomes. The proposed contribution is a falsifiable replication-and-extension protocol for distinguishing transferable faithfulness improvement from metric alignment.

## 1. Introduction

Natural-language explanations are useful only if their apparent reasons bear a defensible relationship to the model decision. A fluent explanation can be plausible to a reader while remaining post-hoc, incomplete or behaviorally irrelevant. Iterative refinement appears to offer a remedy: generate an explanation, critique it and revise it until a faithfulness score improves. Yet the score being optimized is itself an imperfect measurement instrument.

The reviewed literature rules out a broad novelty claim. Wang and Atanasova already use self-critique to refine natural-language explanations, while Zhao and Daumé define prediction–explanation consistency as a necessary faithfulness property. Zaman and Srivastava show that faithfulness metrics can behave differently across models and tasks, making single-score conclusions unsafe. [Wang and Atanasova, 2025, limitation on criterion scope, p. 10](https://aclanthology.org/2025.emnlp-main.427.pdf#page=10); [Zhao and Daumé, 2025, system-level limitation, p. 9](https://aclanthology.org/2025.emnlp-main.797.pdf#page=9); [Zaman and Srivastava, 2025, diagnosticity design, p. 3](https://aclanthology.org/2025.emnlp-main.1496.pdf#page=3).

The closest 2026 work further narrows the opening. FaithLM already combines intervention-based evaluation with iterative explanation optimization. Rao and Layek then show why an answer-change effect needs specificity controls: unrelated filler or simply presenting the answer again can also change a later answer. REFLEX broadens refinement across tasks but explicitly leaves parts of the setting bounded. [FaithLM, 2026, method, p. 4](https://aclanthology.org/2026.eacl-long.177.pdf#page=4); [Rao and Layek, 2026, filler-control design, p. 3](https://aclanthology.org/2026.groundlm-1.35.pdf#page=3); [REFLEX, 2026, scope limitation, p. 15](https://aclanthology.org/2026.acl-long.202.pdf#page=15).

The remaining question is not whether explanations can be refined. It is whether a gain optimized under one measure transfers to an independent measure and exceeds nonspecific intervention effects without degrading task performance.

We ask:

1. **RQ1—Cross-metric transfer:** Does refinement optimized with metric M improve a preregistered held-out faithfulness measure H relative to the original explanation and a neutral rewrite?
2. **RQ2—Specificity:** Does the behavioral effect of the refined explanation exceed effects caused by content-free filler, unrelated text and answer re-injection?
3. **RQ3—Trade-offs:** How do any measured gains relate to answer accuracy, explanation validity, length and human-rated clarity?

The study is diagnostic. A null result, a gain confined to M or an accuracy–faithfulness trade-off would all be informative. We do not claim access to a model's private reasoning.

## 2. Related Work and Gap Establishment

### 2.1 Explanation refinement already exists

SR-NLE iteratively critiques and revises post-hoc explanations using natural-language and attribution feedback. Its authors caution that the selected criteria do not exhaust faithfulness. PEX measures whether an explanation supports the associated prediction, but its reported limitation is that a system-level consistency score cannot establish faithfulness for every individual explanation. These papers motivate refinement and evaluation while also bounding what their metrics warrant. [SR-NLE, operational design, p. 6](https://aclanthology.org/2025.emnlp-main.427.pdf#page=6); [PEX, operational design, p. 4](https://aclanthology.org/2025.emnlp-main.797.pdf#page=4).

Counterfactual-explanation work asks whether a proposed minimal input change actually changes the prediction. Mayne et al. separate validity from minimality and note that invalid generations can be omitted from some minimality calculations, which is why this proposal keeps output validity visible. Dehghanighobadi et al. similarly investigate whether counterfactual explanations align with model behavior. These precedents prevent us from treating “counterfactual” as a single gold standard. [Mayne et al., 2025, evaluation detail, p. 10](https://aclanthology.org/2025.emnlp-main.1231.pdf#page=10).

### 2.2 Metric validity and control conditions are the live gap

Causal Lens constructs faithful–unfaithful pairs to test whether a metric reacts in the intended direction; it also notes that its intervention concerns externally stated explanations rather than unrestricted access to internal computation. FaithLM shows that intervention feedback can drive explanation optimization, but its reported failure analysis includes cases where semantic opposition did not behave as expected. [Zaman and Srivastava, 2025, scope, p. 10](https://aclanthology.org/2025.emnlp-main.1496.pdf#page=10); [FaithLM, 2026, failure analysis, p. 23](https://aclanthology.org/2026.eacl-long.177.pdf#page=23).

Rao and Layek's 2026 audit is the closest methodological constraint. Their filler and re-injection controls show that an observed answer change is not automatically specific to explanation content. They do not claim or test statistical equivalence between controls, so our study will compare paired effect sizes with uncertainty rather than declaring controls equivalent after a nonsignificant test. [Rao and Layek, 2026, statistical limitation, p. 9](https://aclanthology.org/2026.groundlm-1.35.pdf#page=9).

Accordingly, the proposed contribution is the combination of: (a) optimization and evaluation metrics kept separate; (b) matched nonspecific controls; (c) item-paired analysis across refinement rounds; and (d) accuracy, validity and human clarity reported as separate outcomes. Each component has precedent; their use in this bounded cross-metric audit is the contribution to be tested, not assumed.

## 3. Methodology

### 3.1 Tasks, models and sampling

We will use one public natural-language-inference dataset and one public fact-verification dataset with redistributable text and labels. The exact datasets, versions and licenses will be fixed before generation. Two instruction-tuned model families will be selected based on reproducible access and support for recorded inference settings.

For each task–model pair, we plan to sample 120 items that the model answers correctly under the frozen base prompt. Eligibility is therefore conditional on initial correctness; the number screened and the initial accuracy over the screened pool will be reported. This design isolates explanation refinement from answer correction, but limits inference to initially correct decisions.

### 3.2 Explanation and revision conditions

Every eligible item receives an initial answer and explanation. The answer label is then frozen during explanation-only revision; any output that changes it is retained and flagged rather than silently repaired.

| Condition | Revision signal | Purpose |
|---|---|---|
| Initial | None | Baseline explanation |
| Self-critique | Model critiques clarity, evidence use and decision support | Reproduce generic iterative refinement |
| Metric-guided | Critique exposes feedback from optimization metric M | Test direct metric optimization |
| External critique | A frozen separate critic proposes revisions | Separate self-reflection from critic source |
| Neutral rewrite | Match format and approximate length without faithfulness feedback | Control for another generation pass |

Each condition will be collected after one and three rounds. Prompts, metric outputs and full revision histories will be stored. The neutral rewrite will be instructed to preserve meaning and evidence rather than improve a faithfulness criterion.

### 3.3 Measures

Before test results are inspected, one metric will be designated as optimization metric M and at least two nonidentical measures as held-out outcomes. The intended families are:

- prediction–explanation consistency or support;
- a counterfactual or intervention-based behavioral measure;
- a causal-diagnostic score where reproducible implementations permit it.

For intervention tests, each target explanation is paired with:

1. a length-matched content-free filler;
2. unrelated grammatical text matched approximately for length;
3. the original answer re-injected without its explanation; and
4. a no-intervention repeat.

The same model, item and repeat index remain linked. These controls estimate ordinary re-prompting and generic-context sensitivity. They do not reveal true internal reasoning.

Two blinded human raters will evaluate a stratified subset for clarity, relevance and usefulness. They will not label faithfulness, because readability judgments do not provide privileged access to the decision process. Inter-rater agreement, adjudication rules and all exclusions will be reported.

### 3.4 Reproducibility and exclusions

Exact model identifiers, dates, prompts, sampling controls, token limits, parsers and retry rules will be frozen. Invalid JSON, missing explanations, changed labels and technical failures will remain visible in coverage tables. The primary paired set requires a valid initial explanation and all preregistered conditions; an all-available sensitivity analysis will show whether complete-case filtering changes the conclusion.

## 4. Experiments and Evaluation Plan

### 4.1 Primary comparisons

The underlying task item is the resampling unit. The primary RQ1 contrast is the change in held-out measure H from Initial to Metric-guided minus the corresponding change from Initial to Neutral rewrite. A second contrast compares Self-critique with Neutral rewrite. Results will be reported separately by task, model and refinement depth before any pooled summary.

For RQ2, target-intervention answer-change rates will be compared with each control on the same item and repeat index. Paired differences and item-cluster bootstrap intervals will be reported. We will not infer equivalence merely because a difference is nonsignificant.

RQ3 will report task accuracy, changed-answer rate, valid-output coverage, explanation length and human ratings alongside every faithfulness result. These are not combined into a single favorable score.

### 4.2 Interpretation rules fixed in advance

| Observed pattern | Intended interpretation |
|---|---|
| M improves; held-out H does not | Metric alignment, not transferable evidence |
| M and H improve; target effect does not exceed controls | Improvement remains nonspecific |
| M and H improve; target exceeds controls; accuracy retained | Stronger operational evidence, still not proof of private reasoning |
| Faithfulness score improves while accuracy or validity worsens | Trade-off; not an unqualified gain |
| Neutral rewrite matches targeted refinement | Additional generation or formatting may explain the result |

Multiple primary comparisons will be listed and adjusted using a prespecified false-discovery procedure or a smaller confirmatory contrast set. Effect sizes and uncertainty will be emphasized over binary significance.

### 4.3 Feasibility

With two tasks, two models and 120 eligible items per task–model pair, the core sample contains 480 item–model cells. Five explanation conditions at two revision depths, plus intervention controls and repeats, create a substantial inference workload. A 20-item-per-cell pilot will first validate parsing, metric execution and cost. Pilot items will not be reused in the frozen test set if prompts or rules change.

### 4.4 Limitations

The study is limited to selected classification tasks, model families and operational metrics. Refinement may learn to exploit evaluators. The neutral rewrite may not perfectly match semantic or stylistic change. Initial-correctness filtering changes the target population, and behavioral intervention measures can be unstable. Closed-model updates may reduce reproducibility. Human clarity ratings are not faithfulness labels. The study therefore cannot establish a universal explanation metric or identify a model's true reasoning process.

## 5. Conclusion

The reviewed literature already contains iterative explanation refinement, intervention-guided optimization and audits of faithfulness metrics. The defensible next step is not another report that a refinement score rises. This proposal asks whether the gain transfers to a held-out measure, exceeds nonspecific disturbance controls and avoids damage to answer accuracy and output validity. The resulting audit is deliberately capable of rejecting the proposed benefit. Experimental results remain to be collected.

## References

- Samira Dehghanighobadi et al. 2025. [Can LLMs Explain Themselves Counterfactually?](https://aclanthology.org/2025.emnlp-main.396/).
- Yuxia Wang and Pepa Atanasova. 2025. [Self-Critique and Refinement for Faithful Natural Language Explanations](https://aclanthology.org/2025.emnlp-main.427/).
- Jieyu Zhao and Hal Daumé III. 2025. [A Necessary Step toward Faithfulness: Measuring Prediction–Explanation Consistency](https://aclanthology.org/2025.emnlp-main.797/).
- Harry Mayne et al. 2025. [Large Language Models Don't Know Their Own Decision Boundaries](https://aclanthology.org/2025.emnlp-main.1231/).
- Sajjad Zaman and Shashank Srivastava. 2025. [A Causal Lens for Evaluating Faithfulness Metrics](https://aclanthology.org/2025.emnlp-main.1496/).
- 2026. [FaithLM: Towards Faithful Explanations for Large Language Models](https://aclanthology.org/2026.eacl-long.177/).
- Shreyas Rao and Anirban Layek. 2026. [What Does Answer Change Rate Actually Measure?](https://aclanthology.org/2026.groundlm-1.35/).
- 2026. [REFLEX](https://aclanthology.org/2026.acl-long.202/).
