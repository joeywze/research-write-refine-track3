# Cluster 6: research development and proposed evaluation plan

Prepared 5 November 2026. This handover follows full-text review of 17 assigned papers and 3 close 2026 papers. It describes a proposed study; no proposed experiment has been run.

## Working title

**Do Faithfulness Gains Survive the Metric? A Specificity-Controlled Audit of Iterative Explanation Refinement**

## Candidate gap and novelty boundary

Self-refinement, intervention-guided optimization, prediction-explanation consistency and causal metric evaluation already exist. The candidate gap is whether refinement optimized with one metric improves a held-out measure and exceeds ordinary re-prompting, unrelated-text, filler and answer re-injection controls without reducing task accuracy or output validity.

The broad topic is not claimed as new. The proposed contribution is the controlled comparison and reporting protocol described below. Novelty of the exact combination remains provisional pending a wider literature search.

## Research questions

1. **RQ1:** Does improvement on optimization metric M transfer to a preregistered held-out measure H?
2. **RQ2:** Does the target explanation intervention exceed content-free, unrelated-text, answer re-injection and no-intervention controls?
3. **RQ3:** How do any gains relate to task accuracy, changed answers, validity, explanation length and human-rated clarity?

## Proposed study specification

| Component | Proposed choice | Status |
|---|---|---|
| Construct | Self-refinement, intervention-guided optimization, prediction-explanation consistency and causal metric evaluation already exist. The candidate gap is whether refinement optimized with one metric improves a held-out measure and exceeds ordinary re-prompting, unrelated-text, filler and answer re-injection controls without reducing task accuracy or output validity. | Proposed; bounded to this design. |
| Internal literature | 17 assigned full papers, two verified page anchors each. | Complete for the supplied cluster. |
| External challenge set | 3 close 2026 full papers, two verified page anchors each. | Complete for the selected comparison set; wider search pending. |
| Experimental results | None. | Not collected. |
| Team approval | Candidate proposal package. | Pending. |

## Data, controls and collection procedure

1. Use one public natural-language-inference task and one public fact-verification task with fixed licenses and versions.
2. Study two model families and 120 initially correct items per task-model cell, while reporting screening coverage and base accuracy.
3. Compare initial, self-critique, metric-guided, external-critic and neutral-rewrite explanations after one and three rounds.
4. Freeze the answer label during explanation-only revision but retain and flag outputs that nevertheless change it.
5. Keep optimization metric M separate from at least two held-out operational measures from intervention, consistency or counterfactual families.
6. Use blinded human ratings only for clarity, relevance and usefulness, not as privileged faithfulness labels.

All source data, model versions, prompts, settings, exclusions, adjudications, raw outputs and technical failures must be recorded. Pilot material is used to test the procedure; if rules change, those items do not enter the frozen test set.

## Analysis plan

- Primary transfer contrast: change in held-out H for metric-guided refinement minus the corresponding neutral-rewrite change.
- Specificity contrast: paired answer-change effect for the target explanation versus every control on the same item and repeat index.
- Report accuracy, changed-answer rate, valid-output coverage, length and human ratings separately rather than combining them into a favorable score.
- Use item-cluster bootstrap intervals and disclose or adjust multiple primary comparisons.
- Interpret M-only improvement as metric alignment; do not equate a behavioral intervention with access to private reasoning.

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

- Select the two tasks, models and reproducible implementations of M and held-out H.
- Confirm whether model access permits the intended interventions and repeated calls.
- Freeze neutral-rewrite matching, invalid-output treatment and complete-case sensitivity analysis.
- Pilot inference cost and justify the final eligible-item count.

## Handover

Read the [full-text review](review_scope.md), [claim-to-evidence table](claim_evidence_table.md), [external counterevidence](external_evidence.md) and [Draft V0](draft_v0.md) together. The machine-readable [audit ledger](claim_evidence_ledger.json) records source and quote hashes. Approval of this package would authorize refinement of the selected proposal, not imply completed experiments or confirmed novelty.
