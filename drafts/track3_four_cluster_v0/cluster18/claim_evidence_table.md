# Cluster 18: claim-to-evidence table

Prepared 5 November 2026. This table contains 16 full-text paper records and 32 short evidence anchors. Every excerpt was checked against both the saved page extraction and a fresh read from the original PDF. Page numbers are one-based PDF pages.

**Supported by cited passage** means the quoted words and location were verified. It does not mean the reported study was independently reproduced. Reviewer boundaries are interpretations used to constrain this proposal, not extra author claims.

## C01: Understanding and Mitigating Overrefusal in LLM s from an Unveiling Perspective of Safety Decision Boundary

Paper ID: [2025.emnlp-main.1065](https://aclanthology.org/2025.emnlp-main.1065/).

**Attributed claim:** The verified passages provide explicit source anchors for “Multilingual generation scope” and “White-box access limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Multilingual generation scope | “we generate toxic seed prompts in seven languages:” | [3.1 Seed Prompt Generation; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1065.pdf#page=3) |
| White-box access limitation | “RASS requires white-box access to model representations” | [Limitations & Future Work; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1065.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that multilingual overrefusal benchmarking or representation-guided boundary sampling is new without distinguishing its contribution from RASS and MORBench.

## C02: Interpretation Meets Safety: A Survey on Interpretation Methods and Tools for Improving LLM Safety

Paper ID: [2025.emnlp-main.1091](https://aclanthology.org/2025.emnlp-main.1091/).

**Attributed claim:** The verified passages provide explicit source anchors for “Intent excluded from survey scope” and “No quantitative comparison”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Intent excluded from survey scope | “We do not consider user intent (malicious or benign)” | [2 Survey Methodology, footnote 3; PDF p. 2](https://aclanthology.org/2025.emnlp-main.1091.pdf#page=2) |
| No quantitative comparison | “it does not include quantitative comparisons.” | [9 Potential Risks; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1091.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this survey as experimental proof that interpretation-informed guardrails improve multilingual safety or reduce over-refusal.

## C03: M r G uard: A Multilingual Reasoning Guardrail for Universal LLM Safety

Paper ID: [2025.emnlp-main.1392](https://aclanthology.org/2025.emnlp-main.1392/).

**Attributed claim:** The verified passages provide explicit source anchors for “Unsafe-only benchmark scope” and “Human-review limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Unsafe-only benchmark scope | “we thus assume all prompts in these datasets are unsafe.” | [C Dataset Details; PDF p. 13](https://aclanthology.org/2025.emnlp-main.1392.pdf#page=13) |
| Human-review limitation | “we could not scale to multiple annotators or a larger sample size.” | [Limitations — Human Annotation; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1392.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not claim multilingual reasoning guardrails, culturally enriched curricula, code-switching robustness tests, or native-reviewed synthetic-label preservation as unexplored contributions without comparison to this work.

## C04: How Does DPO Reduce Toxicity? A Mechanistic Neuron-Level Analysis

Paper ID: [2025.emnlp-main.1501](https://aclanthology.org/2025.emnlp-main.1501/).

**Attributed claim:** The verified passages provide explicit source anchors for “Toxicity elicitation scope” and “Projection attribution assumption”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Toxicity elicitation scope | “This subset is designed to trigger extremely toxic completions” | [3.1 Data and Models; PDF p. 2](https://aclanthology.org/2025.emnlp-main.1501.pdf#page=2) |
| Projection attribution assumption | “assuming that neurons contribute proportionally along their activated directions” | [8 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1501.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present distributed activation editing or the four-group account of DPO toxicity reduction as novel without distinguishing the proposed contribution from this study.

## C05: Sparse Autoencoder Features for Classifications and Transferability

Paper ID: [2025.emnlp-main.1521](https://aclanthology.org/2025.emnlp-main.1521/).

**Attributed claim:** The verified passages provide explicit source anchors for “Same-language versus cross-lingual classification scope” and “Distributional robustness caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Same-language versus cross-lingual classification scope | “training and testing on the same lan-” | [5.1 Native vs. Cross-Lingual Transfer; PDF p. 6](https://aclanthology.org/2025.emnlp-main.1521.pdf#page=6) |
| Distributional robustness caveat | “its robust- ness under adversarial conditions or domain shifts needs further study.” | [8 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1521.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate toxicity classification F1 with reduced harmful compliance or reduced over-refusal; evaluate generated refusal/compliance behavior separately.

## C06: GRAID : Synthetic Data Generation with Geometric Constraints and Multi-Agentic Reflection for Harmful Content Detection

Paper ID: [2025.emnlp-main.1528](https://aclanthology.org/2025.emnlp-main.1528/).

**Attributed claim:** The verified passages provide explicit source anchors for “Language scope” and “Evaluator bias caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Language scope | “Speciﬁcally, we remove non-English prompts, code snippets,” | [Appendix C: Label Mapping of BeaverTails and WildGuard Sub-categories; PDF p. 16](https://aclanthology.org/2025.emnlp-main.1528.pdf#page=16) |
| Evaluator bias caveat | “dependence on the LLM’s capabilities and potential biases.” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1528.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite these results as evidence of multilingual safety improvement; evaluate specified languages, dialects, registers, and code-switching with qualified native review.

## C07: Language Models Identify Ambiguities and Exploit Loopholes

Paper ID: [2025.emnlp-main.1677](https://aclanthology.org/2025.emnlp-main.1677/).

**Attributed claim:** The verified passages provide explicit source anchors for “Low-risk experimental scope” and “Language coverage limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Low-risk experimental scope | “scenarios that do not include any major risks” | [Ethical Considerations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1677.pdf#page=10) |
| Language coverage limitation | “our experiments are in English only” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1677.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this study as evidence of cross-lingual safety disparities, native-speaker validation, or multilingual over-refusal; those require separate measurements.

## C08: A Simple Yet Effective Method for Non-Refusing Context Relevant Fine-grained Safety Steering in LLM s

Paper ID: [2025.emnlp-main.1781](https://aclanthology.org/2025.emnlp-main.1781/).

**Attributed claim:** The verified passages provide explicit source anchors for “Generic harmless data without paired contrasts” and “Insufficient standalone protection”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Generic harmless data without paired contrasts | “there are no contrastive pairs for the unsafe data” | [4.1 Datasets; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1781.pdf#page=5) |
| Insufficient standalone protection | “it does not reach the reliability required” | [7 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1781.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present non-refusing safety steering or generic-safe-data vector construction as wholly new; compare against SAFE STEER under matched models, extraction data, and intervention budgets.

## C09: Not Your Typical Government Tipline: LLM -Assisted Routing of Environmental Protection Agency Citizen Tips

Paper ID: [2025.emnlp-main.1788](https://aclanthology.org/2025.emnlp-main.1788/).

**Attributed claim:** The verified passages provide explicit source anchors for “Multilingual data scope” and “Historical-label caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Multilingual data scope | “totaling 19,109 tips in multiple languages.” | [4 Methodology; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1788.pdf#page=3) |
| Historical-label caveat | “which may incorporate existing biases or inconsistencies in EPA practice.” | [8 Limitations, (4) Labels as proxy for ground truth; PDF p. 6](https://aclanthology.org/2025.emnlp-main.1788.pdf#page=6) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe jurisdictional filtering errors as measured LLM refusals or treat criminal/civil labels as harmful/benign request labels.

## C10: DSCD : Large Language Model Detoxification with Self-Constrained Decoding

Paper ID: [2025.emnlp-main.197](https://aclanthology.org/2025.emnlp-main.197/).

**Attributed claim:** The verified passages provide explicit source anchors for “MODE-2 retains dynamic safety and hallucination layers” and “Explicit model-generation limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| MODE-2 retains dynamic safety and hallucination layers | “the location of the safety layer and hallucination layer remains dynamic.” | [3.4 MODE-2: Static Toxic Layer; PDF p. 5](https://aclanthology.org/2025.emnlp-main.197.pdf#page=5) |
| Explicit model-generation limitation | “rather than the newer Llama3 series with the same architecture.” | [Limitation; PDF p. 9](https://aclanthology.org/2025.emnlp-main.197.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that training-free decoding guardrails or combined harmful/benign evaluations are novel in themselves; compare against DSCD and relevant hybrid baselines.

## C11: Detoxifying Large Language Models via the Diversity of Toxic Samples

Paper ID: [2025.emnlp-main.298](https://aclanthology.org/2025.emnlp-main.298/).

**Attributed claim:** The verified passages provide explicit source anchors for “Harm-category scope” and “Multilingual scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Harm-category scope | “toxic categories are established based on the ML- Commons taxonomy of hazards” | [3.1.1 Personalized Response Generation Based on Multi-Category Prompts; PDF p. 3](https://aclanthology.org/2025.emnlp-main.298.pdf#page=3) |
| Multilingual scope limitation | “security issues in multimodal and multilingual scenarios.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.298.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim novelty merely for multi-category toxic prompting, self-generated model-specific negatives, or multi-negative preference optimization; DivDetox already combines these elements.

## C12: Automating Steering for Safe Multimodal Large Language Models

Paper ID: [2025.emnlp-main.41](https://aclanthology.org/2025.emnlp-main.41/).

**Attributed claim:** The verified passages provide explicit source anchors for “Binary selective steering” and “Non-monotonic safety control”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Binary selective steering | “activating only when the output score exceeds the specified threshold.” | [3.4 Automatic Adaptive Steering; PDF p. 4](https://aclanthology.org/2025.emnlp-main.41.pdf#page=4) |
| Non-monotonic safety control | “increasing ϵ does not guarantee safer responses.” | [4.4.5 Impact of Steering Intensity ϵ on Output Behavior; PDF p. 8](https://aclanthology.org/2025.emnlp-main.41.pdf#page=8) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present selective inference-time multimodal steering with a trained toxicity probe and refusal head as an entirely new mechanism.

## C13: Refusal-Aware Red Teaming: Exposing Inconsistency in Safety Evaluations

Paper ID: [2025.emnlp-main.49](https://aclanthology.org/2025.emnlp-main.49/).

**Attributed claim:** The verified passages provide explicit source anchors for “Scope includes both refusal error directions” and “Evaluator fallibility”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Scope includes both refusal error directions | “It captures both over-refusal and under-refusal” | [3.1 Problem Formulation; PDF p. 4](https://aclanthology.org/2025.emnlp-main.49.pdf#page=4) |
| Evaluator fallibility | “the Evaluator might yield false positives or negatives” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.49.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not treat model–evaluator disagreement as confirmed model error; independently adjudicate prompt harmfulness and response appropriateness, including evaluator mistakes.

## C14: Toxicity Red-Teaming: Benchmarking LLM Safety in S ingapore’s Low-Resource Languages

Paper ID: [2025.emnlp-main.612](https://aclanthology.org/2025.emnlp-main.612/).

**Attributed claim:** The verified passages provide explicit source anchors for “Adversarial demonstration design” and “Evaluator fallibility”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Adversarial demonstration design | “participant B’s response is intentionally crafted to be toxic.” | [3.1 Toxic Conversation Task; PDF p. 4](https://aclanthology.org/2025.emnlp-main.612.pdf#page=4) |
| Evaluator fallibility | “might make a wrong judgment.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.612.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that Singapore-localized multilingual toxicity red-teaming or comparisons across conversation, QA, and composition are novel without distinguishing the proposed contribution from SGToxicGuard.

## C15: Breaking Bad Tokens: Detoxification of LLM s Using Sparse Autoencoders

Paper ID: [2025.emnlp-main.641](https://aclanthology.org/2025.emnlp-main.641/).

**Attributed claim:** The verified passages provide explicit source anchors for “Non-refusal detoxification objective” and “English-only safety scope”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Non-refusal detoxification objective | “without forcing refusal to user inputs.” | [2.3 Mechanistic Interpretability and Sparse Autoencoders; PDF p. 3](https://aclanthology.org/2025.emnlp-main.641.pdf#page=3) |
| English-only safety scope | “We framed toxicity solely as English-language toxicity” | [8 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.641.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim this paper demonstrates multilingual safety or culturally valid harm labels; evaluate languages and registers explicitly with native or culturally competent reviewers.

## C16: MULTIGUARD : An Efficient Approach for AI Safety Moderation Across Languages and Modalities

Paper ID: [2025.emnlp-main.819](https://aclanthology.org/2025.emnlp-main.819/).

**Attributed claim:** The verified passages provide explicit source anchors for “Representation-based classifier construction” and “External-validity caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Representation-based classifier construction | “After selecting the layer that maximizes the U-Score, we extract embeddings” | [2.2 Fitting a harmfulness classifier; PDF p. 2](https://aclanthology.org/2025.emnlp-main.819.pdf#page=2) |
| External-validity caveat | “its performance in real-world settings might differ.” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.819.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that multilingual or multimodal representation-based guardrails are unexplored; it should compare against this layer-selection and lightweight-classifier approach.
