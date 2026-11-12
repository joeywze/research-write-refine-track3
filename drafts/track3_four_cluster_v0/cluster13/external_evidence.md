# Cluster 13: external evidence and counterevidence

Prepared 5 November 2026. These 4 close 2026 papers were selected because they could invalidate or materially narrow the proposed gap. Their full PDFs were reviewed, not only their abstracts. Each record includes two passages verified against the original PDF.

## E01: Shortcut-Controlled Evaluation for AI-Generated Text Detection

Paper ID: [2026.emnlp-main.2177](https://aclanthology.org/2026.emnlp-main.2177/).

**Problem and method.** The authors investigate whether strong AI-generated text detection results partly reflect benchmark-contingent formatting and lexical shortcuts rather than robust provenance evidence. They examine detector sensitivity when these cues are reduced and introduce an evaluation setting covering raw generation, AI self-editing, and human editing of AI drafts. The authors decompose detection signals into formatting/writing style, lexical usage, and semantic-content flow. They select nine count-based surface features from a broader candidate pool using observed human–AI standardized differences, probe separability with shortcut-only logistic regression and MPNet embeddings plus logistic regression, and compare detectors before and after prompt-based shortcut control.

**Data and experiment.** The diagnostic corpus contains 2,400 human–AI pairs from XSum, SQuAD, WritingPrompts, and PubMedQA. Generators are GPT-5.5, GPT-4, GPT-3.5-Turbo, Gemini 2.5 Pro, Claude Sonnet 4.6, and DeepSeek-V4-Pro; generation uses the first 30 source tokens except for PubMedQA, which uses its question. Additional shortcut-control experiments cover six RAID domains. The linear probes use five-fold cross-validation and report F1, AUROC, and AUPRC. Original-versus-controlled comparisons evaluate DetectGPT, DetectLLM-LRR/NPR, FastDetectGPT, Binoculars, RAIDAR, L2D, MoSEs-Logistic/XGBoost, and BiScope, generally using released implementations and default configurations.

**Author-stated limitation reviewed.** PDF page 9: AIGT-SIGNALBENCH is smaller than large-scale AI-generated text benchmarks despite covering multiple domains and editing variants.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Reference-matched benchmark construction | “The key construction step is reference-matched generation.” | [5.1 Benchmark Construction; PDF p. 7](https://aclanthology.org/2026.emnlp-main.2177.pdf#page=7) |
| Incomplete shortcut removal | “we do not claim to remove all possible shortcuts.” | [Limitations; PDF p. 9](https://aclanthology.org/2026.emnlp-main.2177.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Uses source/reference matching to reduce shortcuts, motivating matched briefs while acknowledging residual confounds.

## E02: Spotlights and Blindspots: Evaluating Machine-Generated Text Detection

Paper ID: [2026.lrec-1.329](https://aclanthology.org/2026.lrec-1.329/).

**Problem and method.** The authors investigate how dataset composition, training domain, evaluation metrics, and decision thresholds affect assessments of machine-generated text detectors. Their central concern is that strong benchmark results may obscure weak generalization and harmful false positives on unfamiliar human writing, making detector comparisons and deployment decisions unreliable. The study evaluates 15 variants from six public detection systems alongside five fine-tuned transformer architectures and two feature-based classifiers. It combines standardized benchmark testing, cross-dataset RoBERTa training, evaluation on exclusively human-authored corpora, artificial class-imbalance experiments, and comparisons of metric-dependent rankings. Additional analysis relates detection errors to text length, punctuation, repetition, and perplexity measured with OPT-1.3B.

**Data and experiment.** The task is binary human-written versus machine-generated text classification, with machine-generated normalized to the positive label. Seven English test sets come from MAGE, including out-of-domain and out-of-domain paraphrase sets; RAID, including adversarial examples; H3C+, covering question answering and semantic-invariant perturbations; and M4GT-Bench. Public systems are Binoculars, Fast-DetectGPT with three variants, Zippy with two variants, RADAR, BiScope with four variants, and DeTeCtive with four variants. Comparators include an all-positive baseline, DistilBERT, BERT, RoBERTa, DeBERTa, Longformer, an n-gram gradient-boosting classifier, and a stylometric ensemble. Initial comparisons use F1 at a default 0.5 threshold and AUROC, followed by precision, recall, accuracy, average recall, and TPR at 1% and 0.01% FPR.

**Author-stated limitation reviewed.** PDF page 9: The evaluation is not exhaustive; many systems and benchmarks fall outside the analysis, so conclusions are bounded by the selected sample.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Cross-dataset evaluation method | “models are trained on one dataset and evaluated on others.” | [4.1. Cross-Training; PDF p. 5](https://aclanthology.org/2026.lrec-1.329.pdf#page=5) |
| Scope limitation | “are necessarily bounded by the scope of our study.” | [9. Limitations; PDF p. 9](https://aclanthology.org/2026.lrec-1.329.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Documents cross-dataset detector blind spots and false positives, blocking a generic robustness claim.

## E03: PAWN++ in the Wild: Evaluating AI-Generated Text Detection on the Web

Paper ID: [2026.wac-1.25](https://aclanthology.org/2026.wac-1.25/).

**Problem and method.** The authors investigate whether strong AI-generated text detection on curated benchmarks transfers to realistic web transformations, frontier generators, multilingual content, and low-false-positive operating points. They also test whether training on a benchmark's generation pipeline produces misleading evidence of general detection capability. PAWN++ trains a 2.7M-parameter classification head over frozen Llama-3.2-1B and Llama-3.2-1B-Instruct probes. It combines token likelihood metrics, cross-model disagreement, uniformly fused hidden layers, learned token weighting, and sequence-level FiLM conditioning. Labels are binary human versus machine, not individual-author identification. The authors introduce WATTLE to evaluate frozen detectors on machine transformations anchored to their original web pages.

**Data and experiment.** MAGE supplies 319,071 training, 56,792 validation, and 60,743 test examples, with additional domain/generator-shift and paraphrase tests. External evaluations use RAID, English and Chinese HC3, and Beemo, including expert- and model-edited outputs. WATTLE contains 41,300 objects: 5,800 generated texts, 34,000 crawl documents including temporal scans, and 1,500 matched human continuation controls. Architecture ablations use identical balanced 5,000-example training and 2,000-example validation subsets, evaluated on the full MAGE test set; full models are selected by validation AUROC. MAGE comparisons largely reproduce published baselines rather than uniformly retraining them. External transfer uses unchanged MAGE-trained weights; RAID specifically evaluates clean RAID-train rows with domain-specific thresholds at a 5% human FPR budget.

**Author-stated limitation reviewed.** PDF page 3: Same-family probe pairs are not claimed to be optimal; heterogeneous pairs remain future work.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Source-matched web evaluation | “Every machine text is paired with the human score” | [8.1 Methods and Protocol; PDF p. 7](https://aclanthology.org/2026.wac-1.25.pdf#page=7) |
| Limits of authorship inference | “should not be treated as standalone proof of authorship” | [Limitations; PDF p. 9](https://aclanthology.org/2026.wac-1.25.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Evaluates realistic human/model web rewrites and warns that detector output is not proof of authorship.

## E04: How Well Does It Generalize? A Robustness Study of Hausa Machine-Generated Text Detection

Paper ID: [2026.winlp-main.5](https://aclanthology.org/2026.winlp-main.5/).

**Problem and method.** The authors investigate whether a high-performing Hausa human-versus-machine news classifier remains reliable beyond its Gemini 2.0 Flash training distribution. They ask whether its original performance replicates across seeds, which genuine human articles it falsely flags, and how detection transfers to other generators. The operational concern is that strong in-distribution accuracy may conceal generator-specific detection and harmful false accusations against Hausa journalists. The authors fine-tune AfroXLMR-large on the released Hausa detection dataset, replicate training across four seeds, and use the seed-42 checkpoint for subsequent error and cross-generator analyses. They compare detection rates and machine-class probabilities with digit and hooked-consonant statistics, conduct an input-Unicode repair ablation, and examine source overlap, detection after 13-gram filtering, and repeated-generation diversity as contamination checks.

**Data and experiment.** The original binary provenance task uses 2,586 human news articles from seven Hausa outlets and 2,586 Gemini 2.0 Flash articles generated from corresponding headlines, with headline-grouped 80/10/10 splits. Cross-generator evaluation adds 260 outputs per condition from Aya-Expanse 8B, Llama 3.1 8B Instruct, Qwen 3 8B, Gemma 4 E4B, Gemma 4 E2B, and NLLB-200 distilled 600M. The primary baseline is Sani et al.'s reported AfroXLMR-large result, not a comparison among multiple detector architectures. Training uses four seeds, maximum sequence length 512, effective batch size 32, and up to eight epochs with validation-F1 early stopping, extending the original three-epoch schedule. Cross-generator tests use the seed-42 checkpoint, matched test headlines, common prompts for chat generators, and Wilson confidence intervals for detection rates.

**Author-stated limitation reviewed.** limitation: The tested model selection supports but does not establish the family-signature hypothesis; multilingual-training-data overlap or shared instruction-tuning corpora remain alternative explanations.; pdf_page: 8

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Actual source of the translation condition | “The Human article was translated” | [Appendix A: Generator prompts; PDF p. 11](https://aclanthology.org/2026.winlp-main.5.pdf#page=11) |
| Single-checkpoint robustness caveat | “Cross-generator evaluation is based on a single seed-42 checkpoint.” | [5.1 Limitations; PDF p. 9](https://aclanthology.org/2026.winlp-main.5.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Directly covers human-edited AI drafts, forcing the proposal toward bidirectional, label-separated histories.

## Gap consequence

Hybrid-text detection, paraphrase attacks, same-generator rewriting, human-edited AI drafts and realistic web rewrites already exist. The candidate gap is a matched bidirectional history that varies original drafter and latest editor independently under identical briefs and revision operations, while keeping original drafter, latest editor and sentence provenance as separate targets.

This comparison set is deliberately challenging rather than exhaustive. A wider search remains required before a definitive novelty claim.
