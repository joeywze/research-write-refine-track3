# Cluster 6: claim-to-evidence table

Prepared 5 November 2026. This table contains 17 full-text paper records and 34 short evidence anchors. Every excerpt was checked against both the saved page extraction and a fresh read from the original PDF. Page numbers are one-based PDF pages.

**Supported by cited passage** means the quoted words and location were verified. It does not mean the reported study was independently reproduced. Reviewer boundaries are interpretations used to constrain this proposal, not extra author claims.

## C01: Transitive self-consistency evaluation of NLI models without gold labels

Paper ID: [2025.emnlp-main.1152](https://aclanthology.org/2025.emnlp-main.1152/).

**Attributed claim:** The verified passages provide explicit source anchors for “Model-label-based evaluation scope” and “English-only limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Model-label-based evaluation scope | “To evaluate the consistency automatically, all NLI labels are provided by” | [3.2 Evaluating Transitive Consistency; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1152.pdf#page=4) |
| English-only limitation | “our current experiments are limited to English-based models and datasets.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1152.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not equate transitive label consistency with explanation faithfulness; it should define and independently test the relationship between explanations and model decisions.

## C02: LLM s Don’t Know Their Own Decision Boundaries: The Unreliability of Self-Generated Counterfactual Explanations

Paper ID: [2025.emnlp-main.1231](https://aclanthology.org/2025.emnlp-main.1231/).

**Attributed claim:** The verified passages provide explicit source anchors for “Independent-context behavioural verification” and “Minimality metric excludes invalid outputs”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Independent-context behavioural verification | “Independent evaluation is essential to avoid bias” | [2 Self-generated counterfactual explanations; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1231.pdf#page=3) |
| Minimality metric excludes invalid outputs | “does not account for the properties of invalid SCEs.” | [7 Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1231.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that validity alone establishes informative or minimal counterfactual explanations; evaluate both and state the distance definition.

## C03: Rule Discovery for Natural Language Inference Data Generation Using Out-of-Distribution Detection

Paper ID: [2025.emnlp-main.1319](https://aclanthology.org/2025.emnlp-main.1319/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational consistency check” and “Explanation reliability caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational consistency check | “Clusters with an average similarity exceeding a predefined threshold” | [3.2.3 Automated Rule Generation and Verification; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1319.pdf#page=5) |
| Explanation reliability caveat | “datasets, and languages remain to be rigorously validated.” | [Limitation; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1319.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must distinguish causal explanation faithfulness from this paper's explanation usefulness, rule overlap, and semantic-consistency criteria; it should not present this study as direct validation of faithful CoT reasoning.

## C04: Sentence Smith: Controllable Edits for Evaluating Text Embeddings

Paper ID: [2025.emnlp-main.1343](https://aclanthology.org/2025.emnlp-main.1343/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational validation scope” and “Metric and ranking validity caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational validation scope | “whether the intended transformation was successfully executed.” | [3.2 Parameterization — Validation; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1343.pdf#page=4) |
| Metric and ranking validity caveat | “rather than on a neutral or universal evaluation of embedding quality.” | [Limitations — On drawing conclusions about embedding model performance; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1343.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present this paper as demonstrating faithful explanations of embedding-model reasoning; it demonstrates transparent input transformations and targeted behavioral evaluation.

## C05: Explaining Differences Between Model Pairs in Natural Language through Sample Learning

Paper ID: [2025.emnlp-main.1462](https://aclanthology.org/2025.emnlp-main.1462/).

**Attributed claim:** The verified passages provide explicit source anchors for “Behavioral evaluation scope” and “Applicability limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Behavioral evaluation scope | “Faithfulness is computed as the fraction of predictions that match” | [3.3 Evaluation Metrics; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1462.pdf#page=5) |
| Applicability limitation | “We evaluate SLED only on classification tasks” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1462.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate agreement/divergence prediction accuracy with causal or mechanistic faithfulness; add targeted feature interventions if making causal claims.

## C06: Do LLM s Behave as Claimed? Investigating How LLM s Follow Their Own Claims using Counterfactual Questions

Paper ID: [2025.emnlp-main.1479](https://aclanthology.org/2025.emnlp-main.1479/).

**Attributed claim:** The verified passages provide explicit source anchors for “Behavioral consistency scope” and “Interaction-scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Behavioral consistency scope | “whether an LLM’s counterfactual claims align with its actual behavior.” | [3.2.2 Constructing the Verification Input from the Original Example; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1479.pdf#page=5) |
| Interaction-scope limitation | “BaC has not yet been applied to long-term or multi-turn interactions” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1479.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim novelty for checking prospective model claims against actual outputs after demonstration-removal interventions without distinguishing the proposal from BaC.

## C07: Graph-Guided Textual Explanation Generation Framework

Paper ID: [2025.emnlp-main.1494](https://aclanthology.org/2025.emnlp-main.1494/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational faithfulness criterion” and “Unexamined internal mechanism”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational faithfulness criterion | “the newly generated NLE should include the inserted word” | [5.1 Faithfulness Evaluation; PDF p. 7](https://aclanthology.org/2025.emnlp-main.1494.pdf#page=7) |
| Unexamined internal mechanism | “the internal mechanisms of the GNN layer remain unexplored” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1494.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A new proposal must not claim that graph-guided use of token or interaction attributions for NLE generation is unexplored; G-TEx already implements and evaluates this approach.

## C08: A Causal Lens for Evaluating Faithfulness Metrics

Paper ID: [2025.emnlp-main.1496](https://aclanthology.org/2025.emnlp-main.1496/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational definition of diagnosticity” and “Framework scope restriction”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational definition of diagnosticity | “measures how often a faithfulness metric prefers faithful over unfaithful explanations.” | [3.1 Diagnosticity; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1496.pdf#page=3) |
| Framework scope restriction | “the metric must be capable of evaluating externally provided explanations.” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1496.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not present metric meta-evaluation using answer-preserving knowledge edits as wholly novel without distinguishing its contribution from CAUSAL DIAGNOSTICITY.

## C09: Extractive Fact Decomposition for Interpretable Natural Language Inference in one Forward Pass

Paper ID: [2025.emnlp-main.1615](https://aclanthology.org/2025.emnlp-main.1615/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational definition of faithful interpretability” and “Scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational definition of faithful interpretability | “it can be traced back to a specific span in the text.” | [5.5 Logical reasoning over spans; PDF p. 6](https://aclanthology.org/2025.emnlp-main.1615.pdf#page=6) |
| Scope limitation | “while hypotheses remain undecomposed.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1615.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A new proposal should not claim novelty merely for encoder-only joint extractive fact decomposition, span-wise NLI, or requiring global–span label agreement.

## C10: L i TE x: A Linguistic Taxonomy of Explanations for Understanding Within-Label Variation in Natural Language Inference

Paper ID: [2025.emnlp-main.1728](https://aclanthology.org/2025.emnlp-main.1728/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational consistency test” and “Explicit-explanation scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational consistency test | “Does the explanation fit the gold label?” | [4.3 Model Generation Validation; PDF p. 7](https://aclanthology.org/2025.emnlp-main.1728.pdf#page=7) |
| Explicit-explanation scope limitation | “It does not account for the implicit reasoning process” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1728.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate this paper's gold-label support judgments with evidence that generated explanations faithfully expose a model's internal decision process; a causal-faithfulness proposal should separately test prediction–explanation dependence.

## C11: Can LLM s Explain Themselves Counterfactually?

Paper ID: [2025.emnlp-main.396](https://aclanthology.org/2025.emnlp-main.396/).

**Attributed claim:** The verified passages provide explicit source anchors for “Context-control design” and “Human-evaluation scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Context-control design | “We denote the validity without context as Val and with context as” | [3.2 Evaluating CEs; PDF p. 4](https://aclanthology.org/2025.emnlp-main.396.pdf#page=4) |
| Human-evaluation scope limitation | “we did not extend this to other tasks.” | [9 Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.396.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim novelty merely for generating self-counterfactual inputs, testing whether they induce target predictions, or comparing evaluation with and without conversation history; this paper already implements those comparisons.

## C12: Self-Critique and Refinement for Faithful Natural Language Explanations

Paper ID: [2025.emnlp-main.427](https://aclanthology.org/2025.emnlp-main.427/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational faithfulness criterion” and “Evaluation scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational faithfulness criterion | “do not contain the intervened word (de- termined by string matching).” | [4.3 Evaluation; PDF p. 6](https://aclanthology.org/2025.emnlp-main.427.pdf#page=6) |
| Evaluation scope limitation | “it reflects only one type of faithfulness criterion.” | [Limitations — Evaluation Method; PDF p. 10](https://aclanthology.org/2025.emnlp-main.427.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that self-critique or attribution-guided refinement for post-hoc explanation faithfulness is unexplored; SR-NLE already implements and evaluates these approaches.

## C13: F in T rust: A Comprehensive Benchmark of Trustworthiness Evaluation in Finance Domain

Paper ID: [2025.emnlp-main.512](https://aclanthology.org/2025.emnlp-main.512/).

**Attributed claim:** The verified passages provide explicit source anchors for “Ownership-disclosure assessment” and “Untested targeted alignment”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Ownership-disclosure assessment | “assess whether it discloses ownership during inference.” | [3.7 Transparency Subset Performance; PDF p. 8](https://aclanthology.org/2025.emnlp-main.512.pdf#page=8) |
| Untested targeted alignment | “We do not perform instruction fine-tuning or alignment” | [Limitations and Ethics; PDF p. 9](https://aclanthology.org/2025.emnlp-main.512.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not claim to introduce the first finance-specific ownership-intervention or conflict-disclosure evaluation; FINTRUST already implements these comparisons.

## C14: Towards Faithful Natural Language Explanations: A Study Using Activation Patching in Large Language Models

Paper ID: [2025.emnlp-main.529](https://aclanthology.org/2025.emnlp-main.529/).

**Attributed claim:** The verified passages provide explicit source anchors for “Explanation scope” and “Intervention coverage limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Explanation scope | “All explanations are generated post-hoc, conditioned on the model’s answer” | [5.1 Dataset and Model; PDF p. 6](https://aclanthology.org/2025.emnlp-main.529.pdf#page=6) |
| Intervention coverage limitation | “activation patching primarily provides insights starting from the corrupted spans onward” | [7 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.529.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A new proposal must not claim novelty merely for comparing answer and explanation causal attributions, incorporating layer-wise alignment, or using activation patching to evaluate post-hoc explanation faithfulness.

## C15: Deriving Strategic Market Insights with Large Language Models: A Benchmark for Forward Counterfactual Generation

Paper ID: [2025.emnlp-main.575](https://aclanthology.org/2025.emnlp-main.575/).

**Attributed claim:** The verified passages provide explicit source anchors for “Evaluation scope” and “Explicit benchmark limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Evaluation scope | “these metrics assess whether counterfactuals reflect plausible future developments” | [3.5 Metrics Design; PDF p. 4](https://aclanthology.org/2025.emnlp-main.575.pdf#page=4) |
| Explicit benchmark limitation | “Our benchmark is currently limited to English- language headlines.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.575.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present this benchmark's counterfactual scenarios as faithful explanations of a financial predictor; a proposal making that claim needs a specified target decision and tests linking explanations to the predictor's behavior.

## C16: Multi-Domain Explainability of Preferences

Paper ID: [2025.emnlp-main.736](https://aclanthology.org/2025.emnlp-main.736/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational evaluation scope” and “Causal faithfulness caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational evaluation scope | “this provides indirect evidence of their faithfulness and utility.” | [4.1 Evaluations; PDF p. 5](https://aclanthology.org/2025.emnlp-main.736.pdf#page=5) |
| Causal faithfulness caveat | “our method is not causal” | [7 Limitations — Causality and Faithfulness; PDF p. 10](https://aclanthology.org/2025.emnlp-main.736.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A new proposal must not present automated concept discovery, shared/domain-specific preference surrogates, concept-guided generation, or explanation-guided tie resolution as unexplored solely on the basis of this paper.

## C17: A Necessary Step toward Faithfulness: Measuring and Improving Consistency in Free-Text Explanations

Paper ID: [2025.emnlp-main.797](https://aclanthology.org/2025.emnlp-main.797/).

**Attributed claim:** The verified passages provide explicit source anchors for “Contrastive consistency operationalization” and “Evaluation granularity limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Contrastive consistency operationalization | “measures how well an explanation supports a given prediction compared to” | [3.2 Measuring Prediction-Explanation (PEX) Consistency; PDF p. 4](https://aclanthology.org/2025.emnlp-main.797.pdf#page=4) |
| Evaluation granularity limitation | “We evaluate explanation faithfulness at the system level” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.797.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that contrastive consistency metrics or PEX-ranked DPO for free-text explanation refinement are new without distinguishing its contribution from this work.
