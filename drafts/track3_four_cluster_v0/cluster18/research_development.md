# Cluster 18: research development and proposed evaluation plan

Prepared 5 November 2026. This handover follows full-text review of 16 assigned papers and 5 close 2026 papers. It describes a proposed study; no proposed experiment has been run.

## Working title

**Safe and Useful Across Singapore Language Settings: A Matched Evaluation of Unsafe Compliance and False Refusal**

## Candidate gap and novelty boundary

Singapore-focused toxicity, multilingual guardrails, over-refusal benchmarks, native-reviewed harmful-prompt sets and refusal mechanisms already exist. The candidate gap is a bounded matched evaluation of harmful and benign near-boundary scenario families in selected Singapore settings, with translation/register disagreement separated from unsafe compliance and false refusal.

The broad topic is not claimed as new. The proposed contribution is the controlled comparison and reporting protocol described below. Novelty of the exact combination remains provisional pending a wider literature search.

## Research questions

1. **RQ1:** How does unsafe-compliance rate on harmful scenarios differ across selected settings?
2. **RQ2:** How does false-refusal rate on benign near-boundary scenarios differ across selected settings?
3. **RQ3:** How much apparent outcome change is concentrated in items with meaning, intent or register disagreement?
4. **RQ4:** Where do an external guardrail and the final model response fail independently or together?

## Proposed study specification

| Component | Proposed choice | Status |
|---|---|---|
| Construct | Singapore-focused toxicity, multilingual guardrails, over-refusal benchmarks, native-reviewed harmful-prompt sets and refusal mechanisms already exist. The candidate gap is a bounded matched evaluation of harmful and benign near-boundary scenario families in selected Singapore settings, with translation/register disagreement separated from unsafe compliance and false refusal. | Proposed; bounded to this design. |
| Internal literature | 16 assigned full papers, two verified page anchors each. | Complete for the supplied cluster. |
| External challenge set | 5 close 2026 full papers, two verified page anchors each. | Complete for the selected comparison set; wider search pending. |
| Experimental results | None. | Not collected. |
| Team approval | Candidate proposal package. | Pending. |

## Data, controls and collection procedure

1. Select English and two additional settings only after recruiting two fluent reviewers and an adjudicator for each.
2. Construct 60 scenario families containing a harmful request, a benign near-boundary request and, where feasible, a clearly benign anchor.
3. Translate and naturally rewrite prompts, then independently label harm status, intent, category, register, naturalness, equivalence and ambiguity.
4. Exclude a complete family from the primary paired analysis when a required member remains non-equivalent or ambiguous under frozen rules.
5. Evaluate two model families and one external input guardrail with three independent calls per model-prompt condition.
6. Use fluent human response labels that separate appropriate refusal, safe redirection, unsafe compliance, safe assistance, false refusal, ambiguity and technical failure.

All source data, model versions, prompts, settings, exclusions, adjudications, raw outputs and technical failures must be recorded. Pilot material is used to test the procedure; if rules change, those items do not enter the frozen test set.

## Analysis plan

- Report unsafe-compliance and false-refusal rates separately; do not collapse them into refusal rate or one accuracy score.
- Use scenario-family paired contrasts and scenario-cluster bootstrap intervals.
- Report repeated-call stability and any unsafe completion without treating calls as independent scenario samples.
- Cross guardrail classification with final response labels to distinguish guardrail- and model-driven failures.
- Analyze disputed-equivalence cases separately and avoid describing a selected setting as inherently safe or unsafe.

### Common reporting requirements

- Report the denominator for every rate and keep invalid outputs, abstentions and technical failures visible.
- Keep repeated generations, translations, variants and revisions linked to their underlying item or scenario.
- Report effect sizes and uncertainty; do not treat a nonsignificant contrast as evidence of equivalence.
- Present subgroup results only when denominators are adequate and were not selected after inspecting favorable outcomes.
- Separate author-reported evidence, reviewer interpretation, proposed design choices and future experimental findings.

## Risks and limitations

- The ACL Anthology corpus and selected 2026 papers are not an exhaustive systematic review.
- Operational metrics do not fully capture the underlying construct and may be gamed or confounded.
- Human review improves label quality but does not create infallible ground truth.
- Small, controlled samples improve traceability but limit external validity.
- Model, API and detector versions can drift after the study is frozen.
- Results apply only to the selected tasks, models, languages/domains and settings.

## Decisions required before approval

- Confirm language settings, fluent reviewers, adjudicator and culturally appropriate compensation.
- Obtain instructor/institutional approval and finalize reviewer-wellbeing and restricted-data procedures.
- Confirm benchmark licenses, harm taxonomy, model/guardrail access and provider-policy compliance.
- Freeze exclusion rules, response rubric and safe-publication boundaries before model evaluation.

## Handover

Read the [full-text review](review_scope.md), [claim-to-evidence table](claim_evidence_table.md), [external counterevidence](external_evidence.md) and [Draft V0](draft_v0.md) together. The machine-readable [audit ledger](claim_evidence_ledger.json) records source and quote hashes. Approval of this package would authorize refinement of the selected proposal, not imply completed experiments or confirmed novelty.
