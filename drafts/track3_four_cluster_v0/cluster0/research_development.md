# Cluster 0: research development and proposed evaluation plan

Prepared 5 November 2026. This handover follows full-text review of 23 assigned papers and 3 close 2026 papers. It describes a proposed study; no proposed experiment has been run.

## Working title

**Fact or Form? A Controlled Invariance Audit of Hallucination Detectors**

## Candidate gap and novelty boundary

Existing work already documents label misalignment, response-length effects, domain shift and detector-family blind spots. The candidate gap is a paired test that holds passage evidence and factual status fixed while answer realization changes. The proposal asks whether within-label score movement across concise, lengthened and paraphrased forms is small relative to the score movement created by a minimal factual error.

The broad topic is not claimed as new. The proposed contribution is the controlled comparison and reporting protocol described below. Novelty of the exact combination remains provisional pending a wider literature search.

## Research questions

1. **RQ1:** Within an item, does each detector rank a supported answer above a minimally incorrect answer?
2. **RQ2:** How much does a detector score vary across meaning-equivalent answer forms with the same factual label?
3. **RQ3:** Is form-induced variation small relative to the correct-incorrect score gap?
4. **RQ4:** Do length, lexical-overlap or semantic-similarity baselines explain comparable behavior?

## Proposed study specification

| Component | Proposed choice | Status |
|---|---|---|
| Construct | Existing work already documents label misalignment, response-length effects, domain shift and detector-family blind spots. The candidate gap is a paired test that holds passage evidence and factual status fixed while answer realization changes. The proposal asks whether within-label score movement across concise, lengthened and paraphrased forms is small relative to the score movement created by a minimal factual error. | Proposed; bounded to this design. |
| Internal literature | 23 assigned full papers, two verified page anchors each. | Complete for the supplied cluster. |
| External challenge set | 3 close 2026 full papers, two verified page anchors each. | Complete for the selected comparison set; wider search pending. |
| Experimental results | None. | Not collected. |
| Team approval | Candidate proposal package. | Pending. |

## Data, controls and collection procedure

1. Use 240 passage-question items from two licensed domains, with a 20-item-per-domain construction pilot.
2. Create one concise supported answer and one minimally incorrect answer per item; the error changes one material entity, quantity, time, polarity or relation.
3. Create concise, meaning-preserving lengthened and approximately length-matched paraphrased forms for each answer.
4. Use two independent passage-grounded labels plus adjudication; remove a complete six-variant item set if a required form does not preserve its intended label.
5. Compare accessible consistency-, uncertainty-, representation- and supervised detectors with length, overlap and semantic-similarity baselines.
6. Freeze detector versions and thresholds on separate calibration material; retain failures and unsupported inputs in coverage tables.

All source data, model versions, prompts, settings, exclusions, adjudications, raw outputs and technical failures must be recorded. Pilot material is used to test the procedure; if rules change, those items do not enter the frozen test set.

## Analysis plan

- Primary discrimination: within-item supported-versus-incorrect ranking and paired score difference.
- Primary invariance: within-answer score range, variance, threshold flip rate and rank preservation across forms.
- Joint diagnostic: form-sensitivity numerator reported beside the correct-incorrect gap; any ratio remains secondary and includes a fixed epsilon.
- Resample whole passage-question items so labels and forms are never treated as independent observations.
- Report domain and detector-family results before pooled summaries; do not infer equivalence from a nonsignificant difference.

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

- Select and license the two QA domains and define the exact supported/incorrect construct.
- Confirm detector implementations, white-box access, compute budget and calibration material.
- Recruit annotators and freeze paraphrase/lengthening validation rules.
- Justify any confirmatory equivalence margin and final sample size.

## Handover

Read the [full-text review](review_scope.md), [claim-to-evidence table](claim_evidence_table.md), [external counterevidence](external_evidence.md) and [Draft V0](draft_v0.md) together. The machine-readable [audit ledger](claim_evidence_ledger.json) records source and quote hashes. Approval of this package would authorize refinement of the selected proposal, not imply completed experiments or confirmed novelty.
