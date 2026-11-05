# Cluster 6: external evidence and counterevidence

Prepared 5 November 2026. These 3 close 2026 papers were selected because they could invalidate or materially narrow the proposed gap. Their full PDFs were reviewed, not only their abstracts. Each record includes two passages verified against the original PDF.

## E01: REFLEX: Self-Refining Explainable Fact-Checking via Verdict-Anchored Style Control

Paper ID: [2026.acl-long.202](https://aclanthology.org/2026.acl-long.202/).

**Problem and method.** The authors investigate verdict-inconsistent, internally contradictory, and misleading natural-language explanations in LLM fact-checking. They frame faithfulness primarily as consistency with instructions, context, and internal logic, rather than demonstrating that an explanation faithfully reconstructs the model’s underlying decision process. Their objective is to improve both verdict prediction and explanation quality without relying on external retrieval or multi-agent interaction. REFLEX first fine-tunes a backbone using dialogue-style supervision to generate verdicts and human-written explanations. It then selects training examples where backbone and fine-tuned verdict correctness disagree: backbone errors corrected by fine-tuning are interpreted as reasoning/style gains, while newly introduced errors are interpreted as knowledge loss. Logistic probes over these groups yield inference vectors and knowledge vectors for decoder-state intervention.

**Data and experiment.** The tasks are verdict classification and natural-language explanation generation on RAW-FC, LIAR-RAW, and AVeriTeC, using human-written rationales. Reported training sizes are 1,612, 6,168, and 2,873 respectively. LIAR-RAW’s six labels are collapsed to three; AVeriTeC’s conflicting-evidence/cherrypicking class is discarded, and its multi-turn instances are flattened. Main baseline comparisons use LLaMA-2-7B against ChatGPT, HiSS, FactLLaMA, L-Defense, and RAV; an appendix also compares DeReC. Ablations cover Qwen-3-8B, a smaller Mistral-v0.1 experiment, evidence and explanation supervision, few-shot sources, alternative cross-stage/objective pairings, cross-dataset transfer, and fact-only/base-only/SFT-only steering directions. Verdicts are evaluated with precision, recall, and Macro-F1.

**Author-stated limitation reviewed.** PDF page 10: Disk quota and experimental scope restrict evaluation to LLaMA-2, Qwen-3, and Mistral-v0.1 at the 7B–8B scale.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational faithfulness scope | “our notion of faithfulness is framed through the lens of” | [Appendix A: Concept Alignment; PDF p. 15](https://aclanthology.org/2026.acl-long.202.pdf#page=15) |
| Internal-knowledge limitation | “Although internal knowledge may become outdated” | [Limitations: Internal Design; PDF p. 10](https://aclanthology.org/2026.acl-long.202.pdf#page=10) |

**Effect on candidate gap - reviewer interpretation.** Shows multi-task explanation refinement is active and limits the proposal to cross-metric transfer plus specificity controls.

## E02: FaithLM: Towards Faithful Explanations for Large Language Models

Paper ID: [2026.eacl-long.177](https://aclanthology.org/2026.eacl-long.177/).

**Problem and method.** The authors investigate how to evaluate and improve post-hoc natural-language explanations of a target LLM’s already-generated answer, including incorrect answers. They distinguish this objective from improving reasoning accuracy or treating chain-of-thought as inherently explanatory. Their motivating problem is that explanation-relevant knowledge may not occur in the input, making input-token removal an inadequate operational test. FaithLM defines faithfulness operationally as prediction sensitivity to an explanation-derived contrary hint. An explainer generates an explanation and an opposite-meaning statement; the latter conditions the unchanged target model, and the resulting prediction shift supplies a fidelity score. Explanation refinement feeds previous explanations and scores back to the explainer, stopping at a decision flip or iteration limit.

**Data and experiment.** Main experiments use the first 500 ECQA instances for commonsense QA, 300 TriviaQA-Long question-answer-evidence triples for reading comprehension, and 500 Balanced COPA causal-reasoning questions. ECQA provides reference explanations for semantic-alignment evaluation. Transfer experiments apply ECQA-optimized prompts to Social-IQA and COPA-optimized prompts to XCOPA. Appendix experiments add MedMCQA and larger target-model evaluations on ECQA and COPA. FaithLM is compared with single-pass SelfExp and chain-of-thought-based Self-consistency, using Vicuna-7B and Phi-2 as main target models and GPT-3.5-Turbo and Claude-2 as explainers and contrary-hint generators. Appendix experiments also use GPT-3.5 and Claude-2 as targets. Results are averaged over three runs; explanation refinement uses up to 20 steps.

**Author-stated limitation reviewed.** PDF page 9, Section 6: Iterative optimization requires additional computation and energy, creating a substantial carbon footprint; the authors call for fewer optimization steps and more sustainable practices.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Operational definition | “faithfulness is defined as prediction sensitivity” | [3.1 Fidelity via Contrary Hint Interventions; PDF p. 4](https://aclanthology.org/2026.eacl-long.177.pdf#page=4) |
| Intervention failure limitation | “when the intervention lacks semantic opposition, fidelity optimization stalls” | [K.3 contrary hint; PDF p. 23](https://aclanthology.org/2026.eacl-long.177.pdf#page=23) |

**Effect on candidate gap - reviewer interpretation.** Establishes intervention-guided explanation optimization, so optimization itself is not the gap.

## E03: What Does Answer Change Rate Actually Measure? A Specificity Audit of Causal Intervention Tests for Explanation Faithfulness

Paper ID: [2026.groundlm-1.35](https://aclanthology.org/2026.groundlm-1.35/).

**Problem and method.** The authors ask whether Answer Change Rate (ACR) following interventions on natural-language explanations measures explanation-specific causal influence or generic sensitivity to prompt disturbance and regeneration. They define faithfulness as explanations causally reflecting the process producing an answer, but audit the validity of a behavioral proxy rather than establish whether particular explanations faithfully describe internal computation. The pipeline first elicits a chain-of-thought explanation and answer, then regenerates the answer under explanation removal, word shuffling, sentence-step reordering, cross-example swapping, length-matched unrelated filler, and original-explanation re-injection. It reports raw ACR, paired floor-adjusted ACR, bootstrap confidence intervals, removal-versus-filler McNemar tests, and correctness-transition breakdowns.

**Data and experiment.** The study uses fixed samples of 500 examples each from GSM8K mathematical reasoning and 16 MMLU-STEM multiple-choice subjects, both English-only. Sample indices are saved before model runs and shared across models. Examples with unparseable original answers are excluded. Stochastic interventions use three seeds; the filler is constructed from one bank of ten mundane sentences and matched to each original explanation's word count. The authors compare six matched base/instruction-tuned pairs: Qwen3-8B, Gemma-7B, Llama-3.1-8B, Qwen2.5-32B, Gemma-2-27B, and Llama-3.1-70B. All use greedy decoding; the 70B pair uses 4-bit quantization. Unrelated filler provides a specificity control, and original-explanation re-injection provides a regeneration baseline.

**Author-stated limitation reviewed.** PDF page 9: Headline rates are empirical rather than universal and may vary across domains, languages, and rationale formats; both evaluation sets are English-only.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Specificity-control scope | “fluent, topic-unrelated filler text of matched length replaces the explanation” | [3.2 Explanation Conditions; PDF p. 3](https://aclanthology.org/2026.groundlm-1.35.pdf#page=3) |
| Limits of non-significant findings | “we apply no formal equivalence test” | [Limitations; PDF p. 9](https://aclanthology.org/2026.groundlm-1.35.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Directly motivates filler and answer re-injection controls and cautions against interpreting answer change as explanation-specific.

## Gap consequence

Self-refinement, intervention-guided optimization, prediction-explanation consistency and causal metric evaluation already exist. The candidate gap is whether refinement optimized with one metric improves a held-out measure and exceeds ordinary re-prompting, unrelated-text, filler and answer re-injection controls without reducing task accuracy or output validity.

This comparison set is deliberately challenging rather than exhaustive. A wider search remains required before a definitive novelty claim.
