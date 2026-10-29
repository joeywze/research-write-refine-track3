# Track 3 Part A: evidence-backed research development

Status: working proposal for Team A review, prepared 20 October 2026. An evidence-backed proposed study is acceptable under the supplied brief and the user's confirmation. No proposed experiments have been conducted, and no results are reported. Proposed methodological choices below are ours; they are not claims made by the cited authors or final group decisions.

## 1. Verify the literature findings

The [targeted review](review_scope.md) covers methods, experimental scope and relevant limitations for all 18 Cluster 7 papers. The [claim-to-evidence table](claim_evidence_table.md) contains 18 attributed claim records and 38 checked excerpts. Quotation checks used saved text and fresh local PDF extraction; they establish source wording, not experimental correctness.

Important corrections and boundaries:

- 138 is a survey, not an original multilingual judge experiment; C03.
- 712 varies judging-instruction language and detail; this is not automatically a response-language comparison; C09.
- 891 and 1307 contain explicit multiple-language settings and must be retained as counterevidence; C12 and C16.
- 625 is explicitly English-only in its limitations; C08 now resolves an earlier excerpt-level Unclear.
- 569 has an additional GenAI-Bench appendix experiment; “exclusively text-only” would be misleading; C06.
- 1534 does not use the dataset's item-level preference labels, but compares with Arena Elo; “no human-derived reference” would be too broad; C17.

These points are traceable to the linked C-records. Language dimensions still lacking explicit supporting evidence remain Unclear. The original automated files have not been silently recoded, and not every statement in those files is certified by this targeted review.

## 2. Create a traceable evidence table

Use the following records as the authoritative evidence trail for this working package:

- [Cluster 7 claim table](claim_evidence_table.md): paper ID, attributed claim, exact passage, page/section, verification status and interpretation boundary.
- [Verification ledger](claim_evidence_ledger.json): matching record IDs, source hashes and page references. This is a working audit format, not a claimed Stage B schema.
- [External evidence](external_evidence.md): E01–E04, including counterevidence and unresolved search leads.

Support means that a source states the attributed point; it does not approve every inference someone might draw from it. A page-specific limitation can justify considering a replication or extension of that study, not a universal claim that a topic is unstudied.

## 3. Narrow and justify the candidate research gap

### What existing studies already cover

| Closest evidence | Established coverage | Consequence for the proposed gap |
|---|---|---|
| Fu and Liu (2025), E01 | Parallel multilingual consistency and correctness evaluation; ground-truth answers used as candidates; English judging instructions. [§§3.3–3.4](https://aclanthology.org/2025.findings-emnlp.587.pdf#page=3). | Neither cross-language consistency nor QA judging is a new topic. Mixed-quality candidates change this setup, but novelty needs other comparisons. |
| Chung and Freienthal (2026), E02 | Controlled dialogue generation and cross-language stability; Estonian human calibration and prompt-language sensitivity check. [§3.5 and limitations](https://aclanthology.org/2026.mme-main.8.pdf#page=4). | Controlled generation and native-language judge prompts already exist. Human reference coverage must be described precisely. |
| Datta and Baitalik (2026), E03 | Multilingual factual QA with correct/incorrect variants; limitations identify one judge and incomplete human validation. [§3.2](https://aclanthology.org/2026.acl-srw.33.pdf#page=3), [limitations](https://aclanthology.org/2026.acl-srw.33.pdf#page=8). | The closest mixed-quality QA baseline. The proposed contribution should emphasize audited replication and a specific human-validation extension, not inventing mixed-quality multilingual QA. |
| Gureja et al. (2025), E04 | Multilingual preference evaluation with sampled native-speaker validation. [§6.3](https://aclanthology.org/2025.acl-long.3.pdf#page=8). | Human-reference multilingual judging is not absent from the field. |
| Cluster 7 C09, C12, C16 | Chinese/English instruction variants, multiple domain-language settings, and six-target-language translation evaluation. | The cluster itself challenges an English-only narrative. |

### Defensible candidate gap—our synthesis, not an author quotation

The verified studies provide several related evaluation designs, but the reviewed passages do not establish performance for the exact study proposed here: context-grounded short QA with matched correct/incorrect variants, independent human reference labels in each selected language, and separate measurements of human agreement, cross-language decision changes and repeated-call stability. We propose a small, transparent replication-and-extension study of this setting. Its combined protocol is a candidate contribution; we have **not established that no other study uses it**.

This is narrower than “multilingual judges are unreliable” and does not predict that a language gap must occur. Finding similar accuracy across languages, stable but incorrect decisions, or disagreement caused by faulty translations would all be informative outcomes. Further screening of the external leads remains necessary before a novelty claim.

### Research questions

- RQ1: Under the same English judging instructions, how does agreement with adjudicated human correctness labels differ between English and one selected language on matched QA content?
- RQ2: How often does the judge change its decision across matched language versions, and how stable are its decisions across repeated calls under fixed settings?
- RQ3, secondary: For the target-language responses, does a meaning-matched target-language rubric change agreement or repeat stability relative to English instructions?

RQ3 is a replication/sensitivity question, not a claim that translated judging prompts are new.

## 4. Define a feasible proposed study

### Scope and decision status

| Element | Proposed working design | Decision status |
|---|---|---|
| Paper type | Evidence-backed proposal; evaluation plan, no fabricated results. | Confirmed by user. |
| Task | Pointwise factual correctness of a short answer against an accompanying passage. Exclude style, helpfulness and overall answer quality from the score. | Proposed; group approval pending. |
| Languages | English plus one language with two fluent raters and bilingual equivalence review available. Select by reviewer access, translatable content and permissible data use, not an unsupported resource label. | Target language open. |
| Data | 20 underlying passage/question items for a feasibility pilot, each with one correct and one deliberately incorrect answer, realized in both languages. Use licensed reusable data or original passages; document provenance. | Item source and licence open. Count is proposed, not a power calculation. |
| Judges | Minimum design: one frozen judge J1 that accepts both languages and exposes reproducible settings. Optional J2 from a different model family for a replication check. Published baselines in E01/E03 provide comparison options, not a claim about present account access. | Exact model/version, access, cost and optional J2 unresolved. No model is approved or executed. |
| Human reference | Two independent ratings per response in its own language, followed by adjudication; retain raw judgments and rationales. | Proposed; raters not recruited. |
| Rubric | Correct / Incorrect / Insufficient evidence, with explicit definitions below. | Proposed; test on separate practice items before freezing. |
| Repetitions | Three calls per judge–response–instruction condition with identical recorded settings; no majority-vote intervention in the primary analysis. | Proposed pilot setting; does not establish broad reliability. |
| Delivery | Research narrative, evidence trail, candidate gap, evaluation plan and provisional V0. | Working handover, not Team A approval or validated Stage B input. |

### Data and human-review procedure

1. Select answerable passage/question items without specialist factual knowledge. Record item IDs, source URL, licence, passage and reference answer. Keep separate practice items for rubric clarification; they are not part of the 20 analysis items.
2. Create a correct answer and a minimally changed incorrect answer per item—for example, change one entity or quantity. A human must check that the incorrect answer is genuinely unsupported or contradicted, not merely a synonym of the correct answer.
3. Translate the passage, question and both answers. A bilingual reviewer checks meaning, naturalness, answerability and preservation of the intended error. Keep a revision log. Identical generation parameters or back-translation alone do not certify equivalence.
4. Freeze the reviewed texts. Present each response separately in randomized order to two fluent raters, blinded to judge outputs and intended correct/incorrect condition. Avoid adjacent paired variants where practical. Record shared bilingual raters if staffing requires them; do not imply four independent people if the same two rate both languages.
5. Adjudicate disagreements from the passage, with a third fluent reviewer if needed. Unresolved items remain unresolved. Exclude a failed or unresolved underlying item and all its language/answer variants from the paired primary analysis; report counts and reasons before examining judge outcomes. Do not quietly repair examples after seeing a judge fail.
6. Record pre-adjudication human agreement. The reference is adjudicated human judgment against the passage, not a new LLM “fact checker” treated as ground truth.

### Shared scoring rubric

| Label | Operational definition |
|---|---|
| Correct | The answer addresses the question, its substantive content is supported by the supplied passage, and it contains no material contradiction or unsupported added claim. Meaning-preserving paraphrases are acceptable. |
| Incorrect | At least one material answer claim contradicts the passage, is unsupported by it, or fails to provide the requested answer. External world knowledge cannot override the supplied passage. |
| Insufficient evidence | The passage/question is ambiguous, incomplete or unreadable enough that correctness cannot be determined. Record a reason; do not force a binary decision. |

Human-unresolved examples are excluded transparently from the primary binary-reference analysis. Judge Insufficient evidence outputs are retained as abstentions, not re-labelled as correct or dropped without reporting coverage. Invalid outputs and technical failures are separate categories. Use the same task definitions for humans and judges; translate instructions with bilingual review rather than changing criteria.

### Conditions and workload

| Response language | Judging instructions | Purpose | Calls for J1 if all items qualify |
|---|---|---|---|
| English | English | Reference condition | 20 × 2 answers × 3 repeats = 120 |
| Target language | English | Primary matched language comparison | 120 |
| Target language | Target language | Secondary instruction-language sensitivity | 120 |

Planned total: 80 response texts, 160 independent human ratings and 360 J1 calls. An optional J2 repeats the same 360-call design, giving 720 calls. Translation checks, adjudication, practice items and technical retries are additional workload. These are arithmetic planning estimates, not observed data, price estimates or evidence that the study is statistically powered.

Keep context, question and answer in the response language. Thus the primary language condition changes all three together; it does not isolate answer language from context/question language. For the primary comparison, keep the English rubric and output format identical apart from the named target language and item fields. Target-language instructions must be meaning-matched and retain the same output-label codes. The secondary contrast holds the target-language response fixed and changes only instruction language. This partial design does not estimate every possible response-language × instruction-language interaction.

Record exact model IDs/versions, provider or hosting details, full prompts, date, sampling controls, token limits, seeds where supported, response order, raw outputs, parsing decisions and failures. Freeze supported settings before collection. Repeated calls measure observed stability under those settings; they are not independent replications of the underlying item sample.

### Analysis plan and interpretation

- **Primary human–judge agreement:** for each response, average its correct-label indicators across the three planned calls, then average across responses within each language/condition. Abstentions, invalid outputs and failed scheduled calls are non-matches in this unconditional metric; report each separately. Compare languages using paired underlying items. Report performance for correct and incorrect reference answers separately.
- **Decision coverage:** fraction of scheduled calls producing a valid Correct/Incorrect decision. Also report conditional binary agreement and Cohen's kappa among such decisions, always beside coverage. If a marginal category is absent and kappa is undefined, report it as undefined rather than zero.
- **Error types:** wrong-answer acceptance = Correct decisions on human-Incorrect responses / scheduled calls on those responses; correct-answer rejection = Incorrect decisions on human-Correct responses / scheduled calls on those responses. Report abstention and failure rates alongside them so apparent error reductions cannot be explained by non-decisions.
- **Repeated-call stability:** proportion of response/condition cells with three identical valid label outputs. Report repeated abstentions separately from repeated Correct/Incorrect decisions. Invalid or missing outputs do not qualify as stable. Stable does not mean correct.
- **Cross-language decision changes:** for each matched item/answer/repeat index under English instructions, report whether both binary decisions exist and, if so, whether they differ. Report the paired-coverage denominator and abstention/failure mismatches separately. Repeat indices are bookkeeping, not independently matched random draws.
- **Human agreement:** raw agreement and Cohen's kappa between the two raters per language before adjudication, plus unresolved and excluded-item counts. These are not directly interchangeable with consensus-reference judge agreement.
- **Uncertainty:** descriptive paired differences and exploratory 95% item-cluster bootstrap intervals, resampling whole underlying items and retaining their translations, answer variants and repeats together. Twenty items may yield wide or degenerate intervals; do not describe a non-significant result as equivalence. A larger confirmatory study would require a justified sample-size plan.

Threats to interpretation include translation artifacts, rater overlap and disagreement, constructed-error realism, small sample size, benchmark contamination and model-version drift. Results would apply only to the selected task, languages, models and settings. Two languages do not support a general causal claim about language-resource levels, and the controlled test is not a deployment-safety certification.

## Handover and next decisions

The [provisional V0](draft_v0.md) follows the brief's six sections. Before Team A sign-off, confirm the target language and raters, data provenance, exact judge configuration and budget, rubric/exclusion rules, and the pending closest-work comparisons. Obtain the actual Stage B package/draft schema before conversion. This Markdown package is not claimed to pass that module's validator.
