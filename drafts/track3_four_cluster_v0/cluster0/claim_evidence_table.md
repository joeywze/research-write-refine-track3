# Cluster 0: claim-to-evidence table

Prepared 5 November 2026. This table contains 23 full-text paper records and 46 short evidence anchors. Every excerpt was checked against both the saved page extraction and a fresh read from the original PDF. Page numbers are one-based PDF pages.

**Supported by cited passage** means the quoted words and location were verified. It does not mean the reported study was independently reproduced. Reviewer boundaries are interpretations used to constrain this proposal, not extra author claims.

## C01: Attention-guided Self-reflection for Zero-shot Hallucination Detection in Large Language Models

Paper ID: [2025.emnlp-main.1063](https://aclanthology.org/2025.emnlp-main.1063/).

**Attributed claim:** The verified passages provide explicit source anchors for “Training-free evaluation scope” and “Failure from query segmentation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Training-free evaluation scope | “there are no training samples.” | [Appendix A: Details of Datasets; PDF p. 11](https://aclanthology.org/2025.emnlp-main.1063.pdf#page=11) |
| Failure from query segmentation | “incorrect segmentation of attentive queries (leading to omission of key information)” | [Appendix I: Bad Cases; PDF p. 12](https://aclanthology.org/2025.emnlp-main.1063.pdf#page=12) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim attention-guided, training-free query perturbation for hallucination detection as wholly new without distinguishing its contribution from AGSER.

## C02: Unsupervised Hallucination Detection by Inspecting Reasoning Processes

Paper ID: [2025.emnlp-main.1124](https://aclanthology.org/2025.emnlp-main.1124/).

**Attributed claim:** The verified passages provide explicit source anchors for “Feature extraction” and “Statement-level scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Feature extraction | “we utilize the last token’s embeddings at the last layer.” | [2.3 Classifier Training; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1124.pdf#page=4) |
| Statement-level scope limitation | “single statements with clear-cut truth values” | [Limitations — Data Coverage; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1124.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim novelty merely for unsupervised confidence-pseudolabeled probing of verification-response activations; IRIS already evaluates this combination.

## C03: Identifying and Answering Questions with False Assumptions: An Interpretable Approach

Paper ID: [2025.emnlp-main.1228](https://aclanthology.org/2025.emnlp-main.1228/).

**Attributed claim:** The verified passages provide explicit source anchors for “Atomic-assumption scope” and “Retrieval dependence”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Atomic-assumption scope | “it requires extracting both explicit and implicit information” | [3.3 Generating and Validating Atomic Assumptions; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1228.pdf#page=5) |
| Retrieval dependence | “The performance of our approach depends on the underlying retrieval system” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1228.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim novelty for retrieving external evidence and generating/validating atomic question assumptions to detect false premises and explain corrections.

## C04: Hallucination Detection in LLM s Using Spectral Features of Attention Maps

Paper ID: [2025.emnlp-main.1239](https://aclanthology.org/2025.emnlp-main.1239/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational hallucination definition” and “Cross-architecture limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational hallucination definition | “label incorrect LLM answers as hallucinations.” | [4.1 Dataset construction; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1239.pdf#page=3) |
| Cross-architecture limitation | “The method is incompatible with LLMs having different head and layer configurations.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1239.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim to introduce the first supervised attention-map or Laplacian-spectral hallucination detector; LapEigvals is a relevant baseline.

## C05: M ed H allu: A Comprehensive Benchmark for Detecting Medical Hallucinations in Large Language Models

Paper ID: [2025.emnlp-main.143](https://aclanthology.org/2025.emnlp-main.143/).

**Attributed claim:** The verified passages provide explicit source anchors for “Construction and retention criterion” and “Corpus coverage limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Construction and retention criterion | “A response is retained only if it deceives at least one” | [4 Implementation Details; PDF p. 5](https://aclanthology.org/2025.emnlp-main.143.pdf#page=5) |
| Corpus coverage limitation | “our hallucination generation pipeline relied on the PubMedQA corpus” | [7 Limitations; PDF p. 8](https://aclanthology.org/2025.emnlp-main.143.pdf#page=8) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that medical hallucination detection benchmarks, difficulty stratification, length matching, source-context judging, or prompted abstention are new without positioning against MedHallu.

## C06: EGOILLUSION : Benchmarking Hallucinations in Egocentric Video Understanding

Paper ID: [2025.emnlp-main.1446](https://aclanthology.org/2025.emnlp-main.1446/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational evaluation metric” and “Auditory scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational evaluation metric | “we report accuracy as the primary metric” | [4 Experimental Setup — Hallucination Evaluation; PDF p. 6](https://aclanthology.org/2025.emnlp-main.1446.pdf#page=6) |
| Auditory scope limitation | “it does not yet cover speech signals.” | [7 Limitation and Future Work; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1446.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not claim to introduce the first egocentric audiovisual hallucination benchmark; it should differentiate its detection target, supervision, modalities, or evaluation protocol from EGOILLUSION.

## C07: Multi-Frequency Contrastive Decoding: Alleviating Hallucinations for Large Vision-Language Models

Paper ID: [2025.emnlp-main.1452](https://aclanthology.org/2025.emnlp-main.1452/).

**Attributed claim:** The verified passages provide explicit source anchors for “Training-free mitigation scope” and “Potential bias amplification”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Training-free mitigation scope | “a plug-and-play technique that requires no training” | [1 Introduction; PDF p. 2](https://aclanthology.org/2025.emnlp-main.1452.pdf#page=2) |
| Potential bias amplification | “may amplify other unknown biases due to contrastive decoding.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1452.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not claim novelty merely for training-free frequency-based contrastive hallucination mitigation or adaptive use of distribution divergence and entropy; MFCD and MFCD-Plus already implement these ideas.

## C08: How Much Do LLM s Hallucinate across Languages? On Realistic Multilingual Estimation of LLM Hallucination

Paper ID: [2025.emnlp-main.1481](https://aclanthology.org/2025.emnlp-main.1481/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detector input scope” and “Synthetic-to-natural error caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detector input scope | “the reference Wikipedia article, prepended to the LLM-generated answer” | [3.2 Multilingual Hallucination Detection — Training; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1481.pdf#page=5) |
| Synthetic-to-natural error caveat | “may not perfectly replicate natural model errors.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1481.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim multilingual span detection, translate-trained hallucination detection, or precision/recall-adjusted multilingual rate estimation as wholly new contributions without distinguishing this study.

## C09: Active Layer-Contrastive Decoding Reduces Hallucination in Large Language Model Generation

Paper ID: [2025.emnlp-main.150](https://aclanthology.org/2025.emnlp-main.150/).

**Attributed claim:** The verified passages provide explicit source anchors for “Operational hallucination-label definition” and “Residual hallucination limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational hallucination-label definition | “contradicts or cannot be supported by trusted references.” | [Appendix A, Step 2: Span-level hallucination annotation; PDF p. 12](https://aclanthology.org/2025.emnlp-main.150.pdf#page=12) |
| Residual hallucination limitation | “ActLCD reduces but does not eliminate hallucinations” | [7 Limitation; PDF p. 9](https://aclanthology.org/2025.emnlp-main.150.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim novelty merely for using internal-layer signals, token-level LLM-derived hallucination labels, or learned adaptive intervention; ActLCD already combines these.

## C10: Where Confabulation Lives: Latent Feature Discovery in LLM s

Paper ID: [2025.emnlp-main.1515](https://aclanthology.org/2025.emnlp-main.1515/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detector input location” and “Prompt and topic dependence”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detector input location | “the activation upstream of the first generated token” | [2.3 Protocol; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1515.pdf#page=4) |
| Prompt and topic dependence | “the extraction is prompt and topic dependent” | [Limitations; PDF p. 8](https://aclanthology.org/2025.emnlp-main.1515.pdf#page=8) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not present pre-generation activation probing or sparse latent steering for unknown-entity confabulation as an unstudied idea.

## C11: Estimating LLM Consistency: A User Baseline vs Surrogate Metrics

Paper ID: [2025.emnlp-main.1554](https://aclanthology.org/2025.emnlp-main.1554/).

**Attributed claim:** The verified passages provide explicit source anchors for “Consistency distinguished from accuracy” and “Length generalization limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Consistency distinguished from accuracy | “consistency might be able to predict accuracy but is fundamentally” | [1 Introduction; PDF p. 2](https://aclanthology.org/2025.emnlp-main.1554.pdf#page=2) |
| Length generalization limitation | “our findings may not generalize to prompts and responses of all lengths.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1554.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe this study’s human labels as factuality or hallucination labels, or its consistency correlations as hallucination-detection performance.

## C12: P rune CD : Contrasting Pruned Self Model to Improve Decoding Factuality

Paper ID: [2025.emnlp-main.1651](https://aclanthology.org/2025.emnlp-main.1651/).

**Attributed claim:** The verified passages provide explicit source anchors for “Benchmark-supervised layer selection” and “Memory caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Benchmark-supervised layer selection | “adopt the MC1 score for assessment.” | [4.2 Factual Layer Search via Ablation; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1651.pdf#page=4) |
| Memory caveat | “it may increase memory footprint due to additional internal activa- tions.” | [Limitations; PDF p. 6](https://aclanthology.org/2025.emnlp-main.1651.pdf#page=6) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe PruneCD as a trained hallucination detector or treat its factuality improvements as detection accuracy; a detection proposal needs explicit prediction units, label definitions, and discrimination/calibration metrics.

## C13: Shallow Focus, Deep Fixes: Enhancing Shallow Layers Vision Attention Sinks to Alleviate Hallucination in LVLM s

Paper ID: [2025.emnlp-main.174](https://aclanthology.org/2025.emnlp-main.174/).

**Attributed claim:** The verified passages provide explicit source anchors for “Method” and “Author-stated limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Method | “broadcasts its attention map across other heads.” | [3.3 Enhancing Attention Vision Sink; PDF p. 5](https://aclanthology.org/2025.emnlp-main.174.pdf#page=5) |
| Author-stated limitation | “improved alignment of projectors and advanced training methods” | [7 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.174.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that shallow attention-sink features are new without distinguishing the proposed detector from this paper's head-count and skewness analyses.

## C14: The Illusion of Progress: Re-evaluating Hallucination Detection in LLM s

Paper ID: [2025.emnlp-main.1761](https://aclanthology.org/2025.emnlp-main.1761/).

**Attributed claim:** The verified passages provide explicit source anchors for “Targeted human validation scope” and “Causal caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Targeted human validation scope | “we intentionally curated a dataset of instances” | [E Additional Analysis of Human Evaluation; PDF p. 13](https://aclanthology.org/2025.emnlp-main.1761.pdf#page=13) |
| Causal caveat | “response length itself is not a direct causal factor” | [N Causality Discussion; PDF p. 18](https://aclanthology.org/2025.emnlp-main.1761.pdf#page=18) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that length baselines or ROUGE-length confounding are novel discoveries; compare new detectors with Len, Mean-Len, and Std-Len under comparable sampling budgets.

## C15: Unconditional Truthfulness: Learning Unconditional Uncertainty of Large Language Models

Paper ID: [2025.emnlp-main.1807](https://aclanthology.org/2025.emnlp-main.1807/).

**Attributed claim:** The verified passages provide explicit source anchors for “Supervised token-confidence learning” and “Cross-task generalization caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Supervised token-confidence learning | “We suggest learning unconditional token-level probability estimates from annotated data.” | [4 Trainable Attention-Based Conditional Dependency; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1807.pdf#page=4) |
| Cross-task generalization caveat | “its generalization across diverse task types remains limited.” | [A.3 Generalization to Out-of-Domain Tasks; PDF p. 17](https://aclanthology.org/2025.emnlp-main.1807.pdf#page=17) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim novelty merely for supervised hallucination detection using attention, token probabilities, or recurrent confidence propagation; TAD already combines these components.

## C16: A Head to Predict and a Head to Question: Pre-trained Uncertainty Quantification Heads for Hallucination Detection in LLM Outputs

Paper ID: [2025.emnlp-main.1809](https://aclanthology.org/2025.emnlp-main.1809/).

**Attributed claim:** The verified passages provide explicit source anchors for “Frozen-generator supervision” and “Limits under confident misinformation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Frozen-generator supervision | “we freeze the “body” of the LLM” | [3.3 Architecture of UQ Heads; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1809.pdf#page=5) |
| Limits under confident misinformation | “Uncertainty heads cannot solve the problem when LLMs are trained” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1809.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim novelty merely for supervised claim-level detection from attention and probability features, transformer-based uncertainty heads, or English-to-other-language detector transfer.

## C17: Calibrating Verbal Uncertainty as a Linear Feature to Reduce Hallucinations

Paper ID: [2025.emnlp-main.187](https://aclanthology.org/2025.emnlp-main.187/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detector inputs” and “Mitigation caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detector inputs | “predicted verbal and semantic uncertainties obtained from two regressor probes.” | [4.1 Hallucination Detection with Semantic and Verbal Uncertainty; PDF p. 5](https://aclanthology.org/2025.emnlp-main.187.pdf#page=5) |
| Mitigation caveat | “does not necessarily lead to correcting hallucinated answers.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.187.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim novelty merely for combining semantic and verbal uncertainty in hallucination detection or for probing question-final hidden states before generation.

## C18: Mitigating Hallucinations in Vision-Language Models through Image-Guided Head Suppression

Paper ID: [2025.emnlp-main.631](https://aclanthology.org/2025.emnlp-main.631/).

**Attributed claim:** The verified passages provide explicit source anchors for “Label definition” and “Deployment limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Label definition | “not present in the ground-truth object set” | [4.2 CHAIR Evaluation; PDF p. 5](https://aclanthology.org/2025.emnlp-main.631.pdf#page=5) |
| Deployment limitation | “It cannot be applied to closed-source or API-based models” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.631.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe SPIN as a supervised or calibrated hallucination detector; a detection proposal should evaluate explicit predictions against independently sourced labels.

## C19: Expanding before Inferring: Enhancing Factuality in Large Language Models through Premature Layers Interpolation

Paper ID: [2025.emnlp-main.645](https://aclanthology.org/2025.emnlp-main.645/).

**Attributed claim:** The verified passages provide explicit source anchors for “Method scope” and “Computational limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Method scope | “PLI usesspherical linear interpolation” | [3 Method; PDF p. 3](https://aclanthology.org/2025.emnlp-main.645.pdf#page=3) |
| Computational limitation | “it introduces additional compu- tational overhead” | [7 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.645.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present training-free internal-layer manipulation for factuality improvement as wholly novel without distinguishing the proposed contribution from PLI.

## C20: The Impact of Negated Text on Hallucination with Large Language Models

Paper ID: [2025.emnlp-main.684](https://aclanthology.org/2025.emnlp-main.684/).

**Attributed claim:** The verified passages provide explicit source anchors for “Paired evaluation scope” and “Generator–judge dependence”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Paired evaluation scope | “Evaluations use pairs of pre-negated and post-negated examples” | [4 Experimental Setup; PDF p. 5](https://aclanthology.org/2025.emnlp-main.684.pdf#page=5) |
| Generator–judge dependence | “both generator and judge could introduce bias” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.684.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not claim novelty merely for evaluating negation robustness in hallucination detection; it should distinguish its contribution from NegHalu's paired label-flipping benchmark and intervention comparisons.

## C21: SHARP : Steering Hallucination in LVLM s via Representation Engineering

Paper ID: [2025.emnlp-main.725](https://aclanthology.org/2025.emnlp-main.725/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detector input” and “Evaluation reproducibility caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detector input | “We analyze the residual stream at the final input position” | [3 Analysis: Diagnosing Hallucination via Representation Separability; PDF p. 3](https://aclanthology.org/2025.emnlp-main.725.pdf#page=3) |
| Evaluation reproducibility caveat | “all reported results are based on a single run.” | [B.3 Implementation Details; PDF p. 13](https://aclanthology.org/2025.emnlp-main.725.pdf#page=13) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that internal-representation probing or cause-specific activation steering for LVLM hallucination is unexplored.

## C22: Pierce the Mists, Greet the Sky: Decipher Knowledge Overshadowing via Knowledge Circuit Analysis

Paper ID: [2025.emnlp-main.781](https://aclanthology.org/2025.emnlp-main.781/).

**Attributed claim:** The verified passages provide explicit source anchors for “Circuit attribution inputs” and “Generalization limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Circuit attribution inputs | “we create a pair of input prompts” | [3.2.2 Knowledge Circuit Construction; PDF p. 4](https://aclanthology.org/2025.emnlp-main.781.pdf#page=4) |
| Generalization limitation | “It remains to be validated whether these conclusions can be directly generalized” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.781.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not treat the paper as establishing broad hallucination-detector superiority; a new detector proposal should report held-out classification metrics, calibration, and appropriate detection baselines.

## C23: Humans Hallucinate Too: Language Models Identify and Correct Subjective Annotation Errors With Label-in-a-Haystack Prompts

Paper ID: [2025.emnlp-main.993](https://aclanthology.org/2025.emnlp-main.993/).

**Attributed claim:** The verified passages provide explicit source anchors for “Candidate-label-conditioned detector input” and “No ground-truth guarantee”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Candidate-label-conditioned detector input | “the query and its candidate label are included in the prompt” | [3 Methodology — Label-in-a-Haystack; PDF p. 3](https://aclanthology.org/2025.emnlp-main.993.pdf#page=3) |
| No ground-truth guarantee | “The model does not provide ground truth / gold labels” | [6 Limitations and Ethics; PDF p. 9](https://aclanthology.org/2025.emnlp-main.993.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe LiaHR as an established detector of factual hallucinations in generated answers; distinguish subjective reasonableness from factual correctness and source faithfulness.
