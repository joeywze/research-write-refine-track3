# External evidence and counterevidence

Reviewed 20 October 2026. These sources are outside the original 18-paper Cluster 7 sample. Exact excerpts below were checked in the primary PDF text supplied by the web reader; unlike the Cluster 7 ledger, this file does not claim a local PDF-hash audit. All pages are one-based PDF pages. Supported means source support, not independent replication.

## E01 — Fu and Liu (2025)

Paper: [How Reliable is Multilingual LLM-as-a-Judge?](https://aclanthology.org/2025.findings-emnlp.587/), Findings of EMNLP, pp. 11040–11053.

| Claim | Exact supporting passage | Location | Status |
|---|---|---|---|
| Ground-truth answers are used as evaluation candidates. | “we select ground truth as evaluated answers.” | [§3.3, p. 3](https://aclanthology.org/2025.findings-emnlp.587.pdf#page=3) | Supported |
| The judging instructions use English. | “we adopt an English prompt” | [§3.3 continued, p. 4](https://aclanthology.org/2025.findings-emnlp.587.pdf#page=4) | Supported |

Context: parallel multilingual tasks, with both correctness and consistency measures in [§§3.2–3.4, pp. 3–4](https://aclanthology.org/2025.findings-emnlp.587.pdf#page=3). Interpretation: a proposed mixed-quality test can differ from this candidate construction, but cross-language consistency is already studied. Do not infer that the paper has no human-derived reference. Its prose and tables differ in model count; this package makes no model-count claim.

## E02 — Chung and Freienthal (2026)

Paper: [Cross-Lingual Stability of LLM Judges Under Controlled Generation: Evidence from Finno-Ugric Languages](https://aclanthology.org/2026.mme-main.8/), MME, pp. 133–148.

| Claim | Exact supporting passage | Location | Status |
|---|---|---|---|
| Human calibration is restricted to one language. | “Human calibration is restricted to Estonian” | [Limitations, p. 5](https://aclanthology.org/2026.mme-main.8.pdf#page=5) | Supported |
| A native-language prompt sensitivity check already exists. | “system prompt translated into Estonian by a native speaker.” | [§3.5, p. 4](https://aclanthology.org/2026.mme-main.8.pdf#page=4) | Supported |

Context: customer-support dialogue evaluation with controlled generation. The limitations acknowledge that remaining discourse-quality differences cannot be fully excluded. Interpretation: fixed generation settings do not by themselves prove semantic equivalence; human review in each selected language is a proposed safeguard, not a new field-wide concept.

## E03 — Datta and Baitalik (2026)

Paper: [Confidence as a Tie-Breaker: Reassessing Multilingual Hedging Bias in LLM-as-a-Judge Evaluation](https://aclanthology.org/2026.acl-srw.33/), ACL Student Research Workshop, pp. 393–402.

| Claim | Exact supporting passage | Location | Status |
|---|---|---|---|
| PolyJudge-Uncertain already varies answer correctness. | “two correctness states, correct and incorrect.” | [§3.2, p. 3](https://aclanthology.org/2026.acl-srw.33.pdf#page=3) | Supported |
| Completed human validation remains a stated limitation of its final rerun. | “final rerun does not yet include completed human validation” | [Limitations, p. 8](https://aclanthology.org/2026.acl-srw.33.pdf#page=8) | Supported |
| The final benchmark uses one judge. | “single judge model” | [Limitations, p. 8](https://aclanthology.org/2026.acl-srw.33.pdf#page=8) | Supported |

Context: controlled short factual QA across English, Hindi, Hinglish and Bengali. Interpretation: adding incorrect answers or multiple languages is not novel by itself. This is a close replication baseline, with human validation a paper-specific extension opportunity.

## E04 — Gureja et al. (2025)

Paper: [M-RewardBench: Evaluating Reward Models in Multilingual Settings](https://aclanthology.org/2025.acl-long.3/), ACL, pp. 43–58.

| Claim | Exact supporting passage | Location | Status |
|---|---|---|---|
| The benchmark covers 23 languages. | “for 23 typologically diverse languages” | [Abstract, p. 1](https://aclanthology.org/2025.acl-long.3.pdf#page=1) | Supported |
| Its human preference-validation results include three named languages. | “results for Hindi, Indonesian, and Spanish.” | [§6.3, p. 8](https://aclanthology.org/2025.acl-long.3.pdf#page=8) | Supported |

Context: translated preference evaluation, including generative reward models, with human checking of sampled preferences. Interpretation: multilingual human-reference evaluation already exists; human annotations in two languages cannot establish novelty. Preference judging and our proposed context-supported correctness task are related but distinct constructs.

## Search scope and leads not yet fully screened

Search date: 20 October 2026. Searches included:

- `multilingual LLM judge human agreement incorrect answers repeated evaluation benchmark`
- `cross lingual LLM judge human annotations instruction language consistency benchmark`
- `"M-RewardBench" multilingual human annotations`
- `"Confidence as a Tie-Breaker" "PolyJudge"`

This was a targeted counterevidence search, not a systematic search with exhaustive coverage. The primary PDFs above were inspected for the cited setup and limitation statements. The following primary-source leads still require methods-level comparison before any novelty sign-off:

- [Rank Reversal in Multilingual LLM Judges: A Label-Free Double-Centering Calibrator](https://arxiv.org/abs/2608.22432), preprint: abstract screened only. Check its human-reference panel, instruction-language conditions and calibration protocol.
- [BabelJudge: Measuring LLM-as-a-Judge Reliability Across Languages and Agent Trajectories](https://arxiv.org/abs/2606.22329), preprint: abstract screened only. Check its language controls, ground-truth construction and consistency definitions.
- [Findings of the WMT25 Multilingual Instruction Shared Task](https://aclanthology.org/2025.wmt-1.23/): abstract screened only. Verify which tasks and languages have human annotations before treating it as a suitable dataset.

No methods or numerical results from these three leads are used to justify the draft. The supported conclusion is that the broad topic has substantial prior work; the novelty of a particular combined protocol remains **Unclear**.
