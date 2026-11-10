# Track 3: four additional evidence-backed Draft V0 proposals

Prepared 5 November 2026. These are proposal-only research packages. No proposed experiments have been run and no results are reported. The original EMNLP 2025 clusters are starting corpora, not exhaustive novelty searches.

## Recommended reading order

| Cluster | Working proposal | Why this is narrower than the obvious topic | Read first |
|---|---|---|---|
| 6 | Do faithfulness gains survive the metric? | Self-critique for explanation faithfulness already exists; the proposal audits whether apparent gains survive held-out metrics and specificity controls. | `cluster6/draft_v0.md` |
| 13 | Origin, editor, or mixture? | Paraphrase attacks, hybrid-text detection and realistic editing benchmarks already exist; the proposal separates original drafter, latest editor and sentence provenance across matched bidirectional histories. | `cluster13/draft_v0.md` |
| 18 | Safe and useful across Singapore language settings | Multilingual safety and multilingual over-refusal already exist; the proposal jointly measures unsafe compliance and false refusal on matched boundary pairs in selected Singapore language settings. | `cluster18/draft_v0.md` |
| 0 | Fact or form? A controlled invariance audit of hallucination detectors | Domain shift and evaluation-label problems already exist; the proposal tests whether detector decisions remain stable when factual status is held fixed and answer form changes. | `cluster0/draft_v0.md` |

Each cluster folder now follows the Cluster 7 research-package structure:

- `README.md`: status, boundaries and reading order;
- `review_scope.md`: full-text methods, experiments and limitations review for every assigned paper;
- `claim_evidence_table.md`: two page-verified evidence anchors per assigned paper;
- `claim_evidence_ledger.json`: machine-readable source, PDF, text and quote hashes;
- `external_evidence.md`: full-text review of the closest 2026 counterevidence;
- `research_development.md`: defensible gap, research questions, design, analysis and decisions required;
- `draft_v0.md`: the narrative proposal.

## Status and boundaries

The revised Draft V0s are grounded in full-text review of all 85 papers assigned to Clusters 0, 6, 13 and 18, plus 15 close 2026 comparison papers. The corpus comprises 100 PDFs and 1,923 pages. Two page-level evidence candidates per paper were rechecked against both extracted page text and a fresh read of the original PDF; all 200 checks passed. The candidate contributions are deliberately described as controlled audits or replication-and-extension studies. None is presented as the first study of its broad topic.

Before selecting a final proposal, the team should confirm data licences, participant/reviewer access, model availability and instructor approval. A wider database search beyond the ACL Anthology corpus remains advisable before making a definitive novelty claim.

## Five-topic handover status

`../track3_five_topic_index.json` is the shared selector index. It includes the
existing reviewed Cluster 7 handover and the four additional topic exports.
Each new cluster contains a `handover/` directory with:

- `research_package.json` and `v0.json` in the shared schema;
- `master_facts.xlsx` for automated fact-checking;
- `export_manifest.json` recording the review boundary.

The four new packages use automated citation-context mappings and are marked
`PROVISIONAL_AUTOMATED_MAPPING` with `production_ready: false`. This avoids a
retrospective manual backfill while keeping their unapproved status visible.
The fact checker is an optional follow-up and does not convert provisional
mappings into reviewed handovers.

Cluster 6 has a completed automated `gpt-6-sol` fact-check run. It remains
provisional: 3 factual statements were labelled `SUPPORTED`, none were labelled
`CONTRADICTED`, and 98 were labelled `INSUFFICIENT_EVIDENCE`. Clusters 0, 13 and
18 have not been run. These model verdicts are triage output, not human approval.
