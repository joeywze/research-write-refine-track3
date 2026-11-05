# Cluster 13: research development and proposed evaluation plan

Prepared 5 November 2026. This handover follows full-text review of 29 assigned papers and 4 close 2026 papers. It describes a proposed study; no proposed experiment has been run.

## Working title

**Origin, Editor, or Mixture? A Bidirectional Revision-History Audit of AI-Text Detectors**

## Candidate gap and novelty boundary

Hybrid-text detection, paraphrase attacks, same-generator rewriting, human-edited AI drafts and realistic web rewrites already exist. The candidate gap is a matched bidirectional history that varies original drafter and latest editor independently under identical briefs and revision operations, while keeping original drafter, latest editor and sentence provenance as separate targets.

The broad topic is not claimed as new. The proposed contribution is the controlled comparison and reporting protocol described below. Novelty of the exact combination remains provisional pending a wider literature search.

## Research questions

1. **RQ1:** How do detector scores move across revision stages within the same document lineage?
2. **RQ2:** Do outputs align more closely with original drafter, latest editor or sentence-level provenance?
3. **RQ3:** Are score changes symmetric for human-origin to AI-edit and AI-origin to human-edit routes under matched operations?
4. **RQ4:** Where do false positives occur on human-origin and human-only revision conditions?

## Proposed study specification

| Component | Proposed choice | Status |
|---|---|---|
| Construct | Hybrid-text detection, paraphrase attacks, same-generator rewriting, human-edited AI drafts and realistic web rewrites already exist. The candidate gap is a matched bidirectional history that varies original drafter and latest editor independently under identical briefs and revision operations, while keeping original drafter, latest editor and sentence provenance as separate targets. | Proposed; bounded to this design. |
| Internal literature | 29 assigned full papers, two verified page anchors each. | Complete for the supplied cluster. |
| External challenge set | 4 close 2026 full papers, two verified page anchors each. | Complete for the selected comparison set; wider search pending. |
| Experimental results | None. | Not collected. |
| Team approval | Candidate proposal package. | Pending. |

## Data, controls and collection procedure

1. Use 40 non-sensitive source briefs in two domains, with identical source packets, required claims and length specifications.
2. Create human-origin and model-origin base drafts using consenting writers and two frozen model configurations.
3. Apply copy-edit, structural, bounded-substantive and controlled sentence-replacement stages.
4. For each origin, include same-type and opposite-type editing routes; preserve tracked diffs and reviewer-marked changed spans.
5. Keep original drafter, latest editor and sentence provenance as noninterchangeable labels; represent mixed documents using provenance proportions.
6. Evaluate likelihood/rank, supervised document, stylistic and contextual sentence detectors with thresholds fixed on separate briefs.

All source data, model versions, prompts, settings, exclusions, adjudications, raw outputs and technical failures must be recorded. Pilot material is used to test the procedure; if rules change, those items do not enter the frozen test set.

## Analysis plan

- Plot raw score trajectories and paired stage changes within each lineage.
- Compare both cross-type directions with their same-type editing controls under the same operation.
- Evaluate association with each target label separately; do not select the label that makes a detector look strongest.
- Treat false positives on original human and human-only revisions as a primary safety outcome.
- Resample source briefs and retain every derived draft, route and stage together.

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

- Select the domains, source-packet licenses, human writers and compensation/withdrawal procedure.
- Confirm model and detector licenses, release permissions and calibration data.
- Freeze revision instructions, effort constraints and semantic-preservation adjudication.
- Define responsible-use language prohibiting forensic or disciplinary interpretation.

## Handover

Read the [full-text review](review_scope.md), [claim-to-evidence table](claim_evidence_table.md), [external counterevidence](external_evidence.md) and [Draft V0](draft_v0.md) together. The machine-readable [audit ledger](claim_evidence_ledger.json) records source and quote hashes. Approval of this package would authorize refinement of the selected proposal, not imply completed experiments or confirmed novelty.
