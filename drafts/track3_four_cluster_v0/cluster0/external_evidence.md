# Cluster 0: external evidence and counterevidence

Prepared 5 November 2026. These 3 close 2026 papers were selected because they could invalidate or materially narrow the proposed gap. Their full PDFs were reviewed, not only their abstracts. Each record includes two passages verified against the original PDF.

## E01: Rethinking Evaluation for LLM Hallucination Detection

Paper ID: [2026.acl-long.680](https://aclanthology.org/2026.acl-long.680/).

**Problem and method.** The authors investigate whether hallucination detection benchmarks support valid evaluation of naturally occurring hallucinations in grounded, long-context QA. They propose seven benchmark desiderata and identify long-context RAG tasks and realistic noisy supervision as major gaps in the benchmarks they review. Their operational target is faithfulness to supplied reference context, not independent factual correctness. The authors introduce TRIVIA+, collecting unmodified answers from three LLMs on reference–question pairs selected using low answer-to-ground-truth ROUGE overlap. Human annotators label sentences as Supported, Contradicted, Not Mentioned, or Supplementary; aggregated sentence votes are converted into binary response labels using the strictest sentence label. Contradicted and Not Mentioned constitute hallucination.

**Data and experiment.** TRIVIA+ contains 3,224 text-only, knowledge-intensive QA instances: 2,101 faithful and 1,123 unfaithful. Sources are TriviaQA, Natural Questions, MS-MARCO, CovidQA, and DROP, spanning general knowledge, web searches, medical documents, and paragraph reasoning. Generators are Gemma-7B, Mixtral-8x7B, and an unnamed commercial 2024 model with more than 150B parameters. Reference contexts average 9.3K characters and reach 94K. The study compares zero-shot Claude-Sonnet-3.5 judging, SelfCheckGPT-NLI with GPT-4-mini or Claude-Sonnet-3.5, three-example few-shot judging, Anthropic-tool prompt optimization, and LoRA instruction tuning of Mistral-7B-Instruct-v0.2; supplementary experiments evaluate ReDeEP with LLaMA-2-7B/13B. Splits are grouped by reference/context to avoid overlap, with an 80/20 training/validation subdivision.

**Author-stated limitation reviewed.** PDF page 10: The definition covers faithfulness to reference context rather than independent factuality; factually correct but unsupported statements can count as hallucinations.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Response-level label aggregation | “keeping the strictest label during aggregation” | [4.2.1 Multi-Vote Annotation for Evaluation Test Labels; PDF p. 6](https://aclanthology.org/2026.acl-long.680.pdf#page=6) |
| Evaluation optimism | “The threshold is optimized to maximize F1 score on the test set.” | [A.2 Model Configuration Details; PDF p. 14](https://aclanthology.org/2026.acl-long.680.pdf#page=14) |

**Effect on candidate gap - reviewer interpretation.** Blocks a generic evaluation-benchmark claim and motivates fixed calibration rather than test-set threshold selection.

## E02: DECK: A Consistency × Confidence Taxonomy of LLM Hallucinations

Paper ID: [2026.findings-aacl.164](https://aclanthology.org/2026.findings-aacl.164/).

**Problem and method.** The authors ask which uncertainty-scoring families can detect different observable forms of LLM factual error. Rather than classifying hallucinations by erroneous content or presumed internal cause, DECK classifies their consistency–confidence signatures and predicts detector blind spots. Operationally, hallucination means a response graded incorrect by dataset-specific deterministic rules; on SelfAware, this specifically means failure to match uncertainty or refusal patterns. DECK crosses inter-sample consistency with token-level confidence to define Drift, Entrenched, Confabulation, and Knotted regimes. Black-box scorers consume sampled responses, white-box scorers consume token probabilities or self-evaluation probabilities, and judges perform factual review. The authors discretize representative black-box and white-box scores using correctness-supervised, within-condition Youden’s J thresholds.

**Data and experiment.** The study evaluates single-turn, short-answer factual QA on TriviaQA, HaluEval QA samples, 500 unanswerable SelfAware questions, and a 499-question PopQA slice. TriviaQA and HaluEval correctness uses normalized reference-answer substring matching; PopQA accepts any matching normalized answer alias. SelfAware correctness uses regex matches for uncertainty/refusal, excluding answerable questions. Across Llama-3-8B, GPT-4o, and Gemini-2.5-Flash, the authors compare six black-box scorers, five white-box scorers, and four judge configurations, including self-, cross-model, and Claude Sonnet 4.6 judges. Multi-generation scorers use five responses at temperature 1.0; top-k probability scorers use k=15. Family representatives are selected by highest AUROC on the target split, and main thresholds are fitted on the full condition.

**Author-stated limitation reviewed.** PDF page 9: Within-condition thresholds remain data-dependent; cross-fitting changes cell shares by up to 12.4 percentage points, and absolute calibrated cutoffs and precision-at-k rules are untested.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational label source | “All grading is deterministic and requires no additional model calls.” | [Appendix B: Response Grading Procedures; PDF p. 13](https://aclanthology.org/2026.findings-aacl.164.pdf#page=13) |
| External-validation caveat | “The test does not control for response correctness” | [Appendix E: External-Signal Validation Protocol; PDF p. 18](https://aclanthology.org/2026.findings-aacl.164.pdf#page=18) |

**Effect on candidate gap - reviewer interpretation.** Shows that consistency and confidence families already have mapped blind spots; motivates family-stratified paired analysis.

## E03: Fortifying Hallucination Detection Under Distribution Shift in Short-Form QA

Paper ID: [2026.findings-emnlp.113](https://aclanthology.org/2026.findings-emnlp.113/).

**Problem and method.** The authors investigate why supervised hallucination detectors that perform well in-domain degrade under distribution shift, and whether heterogeneous general-domain training improves robustness and reduces target-domain labeling requirements. Hallucination is operationalized as an incorrect answer relative to reference answers, rather than a separate assessment of unsupported claims. Distribution shift means cross-dataset or topical shifts within short-form QA, not cross-task transfer. The main detector uses the generating LLM’s middle- and final-layer activations at the last tokens of both the prompt and response. Features are standardized, reduced to 300 dimensions with SVD, and classified by a 100-tree Random Forest. Probability-based features were explored but omitted because they contributed little. The authors compare task-specific training (TS), heterogeneous general training excluding the target dataset (GE), and pooled GE+TS training.

**Data and experiment.** The study pools approximately 697K examples from 12 English QA benchmarks: TriviaQA, Natural Questions, HotpotQA, SQuAD, SimpleQA, WebQuestions, BioASQ, MedQuAD, CoQA, DROP, NewsQA, and OpenLLM. These span encyclopedic, knowledge-base, biomedical, conversational, reasoning, news, and mixed domains, with varying input-context lengths. Responses are open-ended short-form answers. Experiments cover ten generators from Llama, OLMo2, and Qwen2.5 families, primarily 7–8B models with different post-training stages and one 32B OLMo2 model. Single-source experiments train on each of 11 datasets, excluding heterogeneous OpenLLM, and evaluate held-out source and other target datasets. Dataset-level leave-one-out experiments compare GE, TS, and GE+TS against Semantic Entropy, Sindex, GNLL, and PTrue/PFalse.

**Author-stated limitation reviewed.** PDF page 9: Only English datasets are considered, so findings may not generalize to other languages.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational definition of hallucination | “incorrect responses are treated as hallucinations.” | [3 Approach & Experimental Setup — Hallucination in QA setting; PDF p. 3](https://aclanthology.org/2026.findings-emnlp.113.pdf#page=3) |
| Task-scope limitation | “our evaluation is restricted to short form question answering” | [Limitations; PDF p. 9](https://aclanthology.org/2026.findings-emnlp.113.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Blocks a novelty claim based only on distribution shift or heterogeneous training; supports a narrower form-invariance manipulation.

## Gap consequence

Existing work already documents label misalignment, response-length effects, domain shift and detector-family blind spots. The candidate gap is a paired test that holds passage evidence and factual status fixed while answer realization changes. The proposal asks whether within-label score movement across concise, lengthened and paraphrased forms is small relative to the score movement created by a minimal factual error.

This comparison set is deliberately challenging rather than exhaustive. A wider search remains required before a definitive novelty claim.
