# Cluster 13: claim-to-evidence table

Prepared 5 November 2026. This table contains 29 full-text paper records and 58 short evidence anchors. Every excerpt was checked against both the saved page extraction and a fresh read from the original PDF. Page numbers are one-based PDF pages.

**Supported by cited passage** means the quoted words and location were verified. It does not mean the reported study was independently reproduced. Reviewer boundaries are interpretations used to constrain this proposal, not extra author claims.

## C01: Investigating How Pre-training Data Leakage Affects Models’ Reproduction and Detection Capabilities

Paper ID: [2025.emnlp-main.1201](https://aclanthology.org/2025.emnlp-main.1201/).

**Attributed claim:** The verified passages provide explicit source anchors for “Synthetic non-member construction” and “Known-label requirement”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Synthetic non-member construction | “we use GPT-4 to generate paraphrases to create the non-leaked dataset.” | [2.3 Detection Rate; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1201.pdf#page=5) |
| Known-label requirement | “requires that the leakage status of the few-shot examples be known” | [4.1 Mitigation of the Impact of Leakage Rate on Detection Rate; PDF p. 7](https://aclanthology.org/2025.emnlp-main.1201.pdf#page=7) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate training-data membership with AI authorship, or cite the reported detection rates as human-versus-AI classification accuracy.

## C02: What’s in a prompt? Language models encode literary style in prompt embeddings

Paper ID: [2025.emnlp-main.1227](https://aclanthology.org/2025.emnlp-main.1227/).

**Attributed claim:** The verified passages provide explicit source anchors for “Synthetic generator-attribution scope” and “Corpus-size limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Synthetic generator-attribution scope | “prompting GPT4o and GPT4.1 to write novels in 19th century style” | [E.2 Confounding on topic; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1227.pdf#page=10) |
| Corpus-size limitation | “a rather small cor- pus of texts.” | [Limitations; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1227.pdf#page=5) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim novelty merely for probing final-token hidden representations to distinguish literary authors or GPT-4o from GPT-4.1; this paper already demonstrates those settings.

## C03: Profiler: Black-box AI -generated Text Origin Detection via Context-aware Inference Pattern Analysis

Paper ID: [2025.emnlp-main.1265](https://aclanthology.org/2025.emnlp-main.1265/).

**Attributed claim:** The verified passages provide explicit source anchors for “Origin-classification evaluation scope” and “Paraphrase robustness caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Origin-classification evaluation scope | “a one-vs-all setting for each text origin” | [C Additional Experimental Settings; PDF p. 16](https://aclanthology.org/2025.emnlp-main.1265.pdf#page=16) |
| Paraphrase robustness caveat | “performance still degrades on adversarially paraphrased inputs.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1265.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that context-aware black-box generator attribution or provenance testing after paraphrasing is new; distinguish any proposed contribution from PROFILER's loss-window features and self-paraphrase evaluation.

## C04: Speculating LLM s’ C hinese Training Data Pollution from Their Tokens

Paper ID: [2025.emnlp-main.1327](https://aclanthology.org/2025.emnlp-main.1327/).

**Attributed claim:** The verified passages provide explicit source anchors for “Token-level detection scope” and “Unverifiable closed-corpus inference”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Token-level detection scope | “automatically label tokens” | [4 Detect PoC tokens in more vocabularies; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1327.pdf#page=5) |
| Unverifiable closed-corpus inference | “we have no ground truth to verify this estimation” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1327.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present POCDETECT as an AI-generated-text detector or treat its pollution labels as human/AI provenance labels.

## C05: O pen T uring B ench: An Open-Model-based Benchmark and Framework for Machine-Generated Text Detection and Attribution

Paper ID: [2025.emnlp-main.1354](https://aclanthology.org/2025.emnlp-main.1354/).

**Attributed claim:** The verified passages provide explicit source anchors for “Same-generator rewriting scope” and “Language limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Same-generator rewriting scope | “with each model rewriting its own previously generated texts.” | [2.4 Evaluation Tasks, E3; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1354.pdf#page=4) |
| Language limitation | “Our benchmark currently refers only to English texts.” | [Limitations: Language usage; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1354.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that human–AI revision, continuation, same-generator rewriting, domain shift, or unseen-generator evaluation is novel merely by introducing these conditions; this paper already evaluates them.

## C06: Large Language Models Threaten Language’s Epistemic and Communicative Foundations

Paper ID: [2025.emnlp-main.1457](https://aclanthology.org/2025.emnlp-main.1457/).

**Attributed claim:** The verified passages provide explicit source anchors for “Conceptual scope” and “Empirical-grounding limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Conceptual scope | “Our discussion thus far has been primarily conceptual.” | [4 A Framework for Verifiable Provenance; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1457.pdf#page=4) |
| Empirical-grounding limitation | “many of these constructs remain speculative without empirical grounding.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1457.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this paper as an empirical detector benchmark or treat its 70% accuracy statement as a general performance ceiling.

## C07: Machine-generated text detection prevents language model collapse

Paper ID: [2025.emnlp-main.1506](https://aclanthology.org/2025.emnlp-main.1506/).

**Attributed claim:** The verified passages provide explicit source anchors for “Unknown-provenance mixed-data scope” and “Detector transfer caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Unknown-provenance mixed-data scope | “the origin of each training sample is unknown” | [6 Preventing model collapse; PDF p. 6](https://aclanthology.org/2025.emnlp-main.1506.pdf#page=6) |
| Detector transfer caveat | “we observed a drop in detection performance compared to GPT-2 text” | [B.3 Dataset; PDF p. 14](https://aclanthology.org/2025.emnlp-main.1506.pdf#page=14) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim novelty solely for using machine-generated-text detection to curate mixed training data or mitigate recursive model degradation; this paper already implements and evaluates that approach.

## C08: S im M ark: A Robust Sentence-Level Similarity-Based Watermarking Algorithm for Large Language Models

Paper ID: [2025.emnlp-main.1567](https://aclanthology.org/2025.emnlp-main.1567/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detection scope” and “Mixed-content limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detection scope | “text is likely generated by an LLM watermarked by SimMark.” | [3.2 Watermarked Text Detection, Algorithm 2; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1567.pdf#page=5) |
| Mixed-content limitation | “watermarked text is interleaved with or embedded” | [Limitations: Resistance to More Advanced Attacks; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1567.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present watermark absence as evidence of human authorship; distinguish human text, unwatermarked AI text, and SimMark-watermarked text in labels and evaluation.

## C09: Same Question, Different Words: A Latent Adversarial Framework for Prompt Robustness

Paper ID: [2025.emnlp-main.1595](https://aclanthology.org/2025.emnlp-main.1595/).

**Attributed claim:** The verified passages provide explicit source anchors for “Study scope” and “Fine-tuning limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Study scope | “we primarily focus on query paraphrasing robustness.” | [2 Related Work; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1595.pdf#page=3) |
| Fine-tuning limitation | “do not perform experiments with other PEFT techniques” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1595.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe LAP's preference win-rates as detection accuracy, calibrated provenance probabilities, or evidence of low false-positive rates.

## C10: T emp P araphraser: “Heating Up” Text to Evade AI -Text Detection through Paraphrasing

Paper ID: [2025.emnlp-main.1607](https://aclanthology.org/2025.emnlp-main.1607/).

**Attributed claim:** The verified passages provide explicit source anchors for “Interpretation of the headline detection metric” and “Sentence-level coherence limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Interpretation of the headline detection metric | “used in the paper is equivalent to recall.” | [E.1 Additional Metrics for Evaluating Attack Effectiveness; PDF p. 16](https://aclanthology.org/2025.emnlp-main.1607.pdf#page=16) |
| Sentence-level coherence limitation | “which may result in a loss of long-range contextual coherence” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1607.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not claim that paraphrasing robustness, temperature sensitivity, or paraphrase-based detector augmentation is unexplored; distinguish the proposed contribution from these experiments.

## C11: Are Generative Models Underconfident? Better Quality Estimation with Boosted Model Probability

Paper ID: [2025.emnlp-main.166](https://aclanthology.org/2025.emnlp-main.166/).

**Attributed claim:** The verified passages provide explicit source anchors for “Method scope” and “Weak-model limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Method scope | “we use the total probability mass of the dominant cluster.” | [4 BOOSTED PROB; PDF p. 4](https://aclanthology.org/2025.emnlp-main.166.pdf#page=4) |
| Weak-model limitation | “it might emphasize weak models’ overconfidence.” | [8 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.166.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this paper as demonstrating human-versus-AI detection or authorship attribution; quality labels and provenance labels require separate operational definitions.

## C12: From Shortcuts to Balance: Attribution Analysis of Speech-Text Feature Utilization in Distinguishing Original from Machine-Translated Texts

Paper ID: [2025.emnlp-main.1665](https://aclanthology.org/2025.emnlp-main.1665/).

**Attributed claim:** The verified passages provide explicit source anchors for “Attribution-analysis scope” and “Translation-system coverage limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Attribution-analysis scope | “attribution analysis concerns solely sentences containing NEs.” | [3 Experimental Setup; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1665.pdf#page=3) |
| Translation-system coverage limitation | “using one widely-used transla- tion system” | [Limitations; PDF p. 5](https://aclanthology.org/2025.emnlp-main.1665.pdf#page=5) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate original-versus-machine-translated labels with general human-versus-AI authorship, or claim detection of mixed authorship, post-editing, or paraphrasing from these experiments.

## C13: Leveraging Multilingual Training for Authorship Representation: Enhancing Generalization across Languages and Domains

Paper ID: [2025.emnlp-main.1766](https://aclanthology.org/2025.emnlp-main.1766/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detection label scope” and “Non-English domain limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detection label scope | “requires distinguishing between human-written and machine-generated texts.” | [6.5 Machine-Generated Text Detection; PDF p. 8](https://aclanthology.org/2025.emnlp-main.1766.pdf#page=8) |
| Non-English domain limitation | “our multilingual dataset is sourced from a single domain: Wikipedia.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1766.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that multilingual authorship representations have never been evaluated for AI-generated text detection; this paper evaluates that combination on MULTITuDE.

## C14: so much depends / upon / a whitespace: Why Whitespace Matters for Poets and LLM s

Paper ID: [2025.emnlp-main.1783](https://aclanthology.org/2025.emnlp-main.1783/).

**Attributed claim:** The verified passages provide explicit source anchors for “Prompt-condition scope” and “Geographic representativeness limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Prompt-condition scope | “a simplified prompt that does not mention whitespace” | [4.2 LLM-Generated Poems; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1783.pdf#page=4) |
| Geographic representativeness limitation | “These poems overrepresent poets from the North American region.” | [9 Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.1783.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not present this study as demonstrating an effective AI-poetry detector or calibrated authorship probabilities; its benchmark measures extraction fidelity, not detection.

## C15: Certified Mitigation of Worst-Case LLM Copyright Infringement

Paper ID: [2025.emnlp-main.1784](https://aclanthology.org/2025.emnlp-main.1784/).

**Attributed claim:** The verified passages provide explicit source anchors for “Black-box inference-time scope” and “Limits of literal-copy mitigation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Black-box inference-time scope | “requires only black-box access to the generation model” | [3.2 BLOOM SCRUB; PDF p. 4](https://aclanthology.org/2025.emnlp-main.1784.pdf#page=4) |
| Limits of literal-copy mitigation | “eliminating direct quotations alone is a necessary but not sufficient condition” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1784.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate corpus quotation detection with AI-authorship attribution; define source overlap, provenance, and human/AI authorship as distinct targets.

## C16: Retracing the Past: LLM s Emit Training Data When They Get Lost

Paper ID: [2025.emnlp-main.1789](https://aclanthology.org/2025.emnlp-main.1789/).

**Attributed claim:** The verified passages provide explicit source anchors for “Attack scope” and “Entropy caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Attack scope | “untargeted data extraction attacks on white-box models” | [2 Related Work; PDF p. 3](https://aclanthology.org/2025.emnlp-main.1789.pdf#page=3) |
| Entropy caveat | “its universal sufficiency is not yet established.” | [7 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.1789.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Define generation mechanism, original source authorship, and document editing history separately; corpus overlap alone must not be treated as an AI-authorship label.

## C17: OBLIVIATE : Robust and Practical Machine Unlearning for Large Language Models

Paper ID: [2025.emnlp-main.183](https://aclanthology.org/2025.emnlp-main.183/).

**Attributed claim:** The verified passages provide explicit source anchors for “Method: parameter-efficient unlearning” and “Caveat: degraded generation quality”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Method: parameter-efficient unlearning | “we thus apply LoRA to fine-tune the MLP and MHA layers” | [3.3 Tailored Unlearning Loss; PDF p. 5](https://aclanthology.org/2025.emnlp-main.183.pdf#page=5) |
| Caveat: degraded generation quality | “ours occasionally gener- ated gibberish or even blank outputs” | [6 Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.183.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this paper as an AI-text detector or treat membership inference, DRMA, or TOFU fictional-author profiles as human/AI authorship labels.

## C18: S en D et EX : Sentence-Level AI -Generated Text Detection for Human- AI Hybrid Content via Style and Context Fusion

Paper ID: [2025.emnlp-main.268](https://aclanthology.org/2025.emnlp-main.268/).

**Attributed claim:** The verified passages provide explicit source anchors for “Binary provenance prediction” and “Context dependence”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Binary provenance prediction | “predict the probability of being AI-generated” | [3.3 Information Fusion Module; PDF p. 5](https://aclanthology.org/2025.emnlp-main.268.pdf#page=5) |
| Context dependence | “Its advantage will diminish in sparse or noisy context” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.268.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that irregular sentence-level mixing or style–context fusion is unexplored; it should distinguish its contribution from this benchmark and framework.

## C19: M o SE s: Uncertainty-Aware AI -Generated Text Detection via Mixture of Stylistics Experts with Conditional Thresholds

Paper ID: [2025.emnlp-main.294](https://aclanthology.org/2025.emnlp-main.294/).

**Attributed claim:** The verified passages provide explicit source anchors for “Conditional decision threshold” and “Binary detection scope”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Conditional decision threshold | “Cβin Equation (2) is actually the estimated threshold.” | [3.4 Conditional Threshold Estimator; PDF p. 5](https://aclanthology.org/2025.emnlp-main.294.pdf#page=5) |
| Binary detection scope | “The current study focuses on binary detection.” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.294.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not equate binary corpus source labels with verified individual authorship, misconduct, or complete provenance; it should explicitly define how human-prompted continuations, mixed authorship, and edited documents are labeled.

## C20: Context-Aware Membership Inference Attacks against Pre-trained Large Language Models

Paper ID: [2025.emnlp-main.370](https://aclanthology.org/2025.emnlp-main.370/).

**Attributed claim:** The verified passages provide explicit source anchors for “Membership rather than authorship scope” and “Calibration-data dependency”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Membership rather than authorship scope | “Our work remains at the instance-level, selectively using tokens within a sample” | [6 Additional related works; PDF p. 9](https://aclanthology.org/2025.emnlp-main.370.pdf#page=9) |
| Calibration-data dependency | “Our attack requires access to non-member data for calibration purposes.” | [9 Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.370.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate training-set membership with AI authorship; define these as separate provenance labels and evaluation tasks.

## C21: Genre Matters: How Text Types Interact with Decoding Strategies and Lexical Predictors in Shaping Reading Behavior

Paper ID: [2025.emnlp-main.379](https://aclanthology.org/2025.emnlp-main.379/).

**Attributed claim:** The verified passages provide explicit source anchors for “Method” and “Human baseline limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Method | “For the analyses, we utilize linear mixed-effects models” | [3.3 Methods; PDF p. 4](https://aclanthology.org/2025.emnlp-main.379.pdf#page=4) |
| Human baseline limitation | “it does not include human-written baselines” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.379.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this study as evidence that eye movements, surprisal, or readability reliably distinguish human from AI authorship; it lacks a human-written comparison condition and an authorship detection task.

## C22: Your Language Model Can Secretly Write Like Humans: Contrastive Paraphrase Attacks on LLM -Generated Text Detectors

Paper ID: [2025.emnlp-main.433](https://aclanthology.org/2025.emnlp-main.433/).

**Attributed claim:** The verified passages provide explicit source anchors for “Training-free paraphrase scope” and “Language limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Training-free paraphrase scope | “a training-free paraphrase approach named Contrastive Paraphrase Attack” | [1 Introduction; PDF p. 2](https://aclanthology.org/2025.emnlp-main.433.pdf#page=2) |
| Language limitation | “focuses exclusively on English text” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.433.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A new proposal should not claim that training-free contrastive paraphrasing or surrogate-free whole-passage evasion is unexplored; CoPA supplies a direct prior baseline.

## C23: A Fully Probabilistic Perspective on Large Language Model Unlearning: Evaluation and Optimization

Paper ID: [2025.emnlp-main.452](https://aclanthology.org/2025.emnlp-main.452/).

**Attributed claim:** The verified passages provide explicit source anchors for “Joint input-output evaluation scope” and “Scalability limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Joint input-output evaluation scope | “both input and output distributions are considered.” | [4.2 Fully Probabilistic Evaluation Framework; PDF p. 4](https://aclanthology.org/2025.emnlp-main.452.pdf#page=4) |
| Scalability limitation | “The scalability of our methods to more extensive datasets also remains a” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.452.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this paper as an AI-text detector or as evidence that a detector distinguishes human, AI, and mixed-authorship text.

## C24: Enhancing LLM Text Detection with Retrieved Contexts and Logits Distribution Consistency

Paper ID: [2025.emnlp-main.503](https://aclanthology.org/2025.emnlp-main.503/).

**Attributed claim:** The verified passages provide explicit source anchors for “Detection method” and “Generation-instruction limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Detection method | “leveraging the distribution consistency of input text” | [2.1 LLM Text Detection; PDF p. 3](https://aclanthology.org/2025.emnlp-main.503.pdf#page=3) |
| Generation-instruction limitation | “may be related to the instruction used to generate detected text” | [Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.503.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal should not claim that using retrieved human-written and LLM-rewritten contexts, or their distribution consistency, is novel without distinguishing its contribution from HALO.

## C25: Layered Insights: Generalizable Analysis of Human Authorial Style by Leveraging All Transformer Layers

Paper ID: [2025.emnlp-main.521](https://aclanthology.org/2025.emnlp-main.521/).

**Attributed claim:** The verified passages provide explicit source anchors for “Single-author collection scope” and “Language-transfer limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Single-author collection scope | “each written by a single author” | [4 Experiment setup — Task; PDF p. 3](https://aclanthology.org/2025.emnlp-main.521.pdf#page=3) |
| Language-transfer limitation | “our findings might not be transferable to other languages” | [8 Limitations; PDF p. 9](https://aclanthology.org/2025.emnlp-main.521.pdf#page=9) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not describe LIGHT as an evaluated human-versus-AI detector or treat same-author labels as equivalent to generation-provenance labels.

## C26: Primus: A Pioneering Collection of Open-Source Datasets for Cybersecurity LLM Training

Paper ID: [2025.emnlp-main.527](https://aclanthology.org/2025.emnlp-main.527/).

**Attributed claim:** The verified passages provide explicit source anchors for “Classifier label scope” and “Cross-corpus classifier caveat”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Classifier label scope | “distinguish cybersecurity-related text from non-cybersecurity text” | [2.3.1 Cybersecurity Classifier; PDF p. 4](https://aclanthology.org/2025.emnlp-main.527.pdf#page=4) |
| Cross-corpus classifier caveat | “likely because our classifier was trained on FineWeb.” | [C PRIMUS-NEMOTRON-CC; PDF p. 16](https://aclanthology.org/2025.emnlp-main.527.pdf#page=16) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite PRIMUS as a human-versus-AI text detection benchmark or its relevance classifier as an authorship detector.

## C27: Beyond Checkmate: Exploring the Creative Choke Points for AI Generated Texts

Paper ID: [2025.emnlp-main.600](https://aclanthology.org/2025.emnlp-main.600/).

**Attributed claim:** The verified passages provide explicit source anchors for “Paired-selection task scope” and “Segmentation limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Paired-selection task scope | “identifying the AI text from a given (human, AI) pair.” | [4.2 Checkmating AI text: which segment reveals its origins?; PDF p. 8](https://aclanthology.org/2025.emnlp-main.600.pdf#page=8) |
| Segmentation limitation | “alternative approaches may yield different results.” | [Limitations; PDF p. 10](https://aclanthology.org/2025.emnlp-main.600.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: A proposal must not claim that segment-aware detection or cross-segment stylistic variation is unexplored; this paper directly evaluates both.

## C28: Unraveling Interwoven Roles of Large Language Models in Authorship Privacy: Obfuscation, Mimicking, and Verification

Paper ID: [2025.emnlp-main.753](https://aclanthology.org/2025.emnlp-main.753/).

**Attributed claim:** The verified passages provide explicit source anchors for “AI-text detection scope” and “Human-evaluation limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| AI-text detection scope | “we employ GPTZero” | [5.3 Triplet-wise Interdependency: Anthropomorphism Analysis; PDF p. 8](https://aclanthology.org/2025.emnlp-main.753.pdf#page=8) |
| Human-evaluation limitation | “limited by the absence of human-centered evalua- tion.” | [Limitation; PDF p. 10](https://aclanthology.org/2025.emnlp-main.753.pdf#page=10) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not equate target-author verification accuracy or its false positives with human-versus-AI detection accuracy or false accusations of human writers; define these labels separately.

## C29: Friend or Foe? A Computational Investigation of Semantic False F riends across R omance Languages

Paper ID: [2025.emnlp-main.773](https://aclanthology.org/2025.emnlp-main.773/).

**Attributed claim:** The verified passages provide explicit source anchors for “Actual detection target” and “Synchronic scope limitation”.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Actual detection target | “we implement false friend detection as a binary classifier” | [3.2 False Friends Detection; PDF p. 4](https://aclanthology.org/2025.emnlp-main.773.pdf#page=4) |
| Synchronic scope limitation | “the synchronic approach is inherently limited in its ability to track historical” | [6 Conclusions and Future Directions; PDF p. 7](https://aclanthology.org/2025.emnlp-main.773.pdf#page=7) |

**Verification status:** Supported by cited passage; exact wording matched in extracted text and the original PDF.

**Reviewer boundary:** Reviewer interpretation: Do not cite this paper's detection scores as evidence for AI-authorship or provenance detection; its prediction units and labels are lexical-semantic.
