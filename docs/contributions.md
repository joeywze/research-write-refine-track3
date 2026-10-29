# Contributions and integration provenance

## Team workstreams

| Workstream | Contributors |
|---|---|
| Research development, evidence checking and handover | Tabitha / Joey / Silvia |
| Writing refinement, interface and evaluation tools | Guan Hong / Wan Yun / Lili |
| Integration, validation and final deliverables | Entire team |

These are the team's supplied workstream assignments, not a replacement for Git's per-commit authorship records.

## Integrated source revisions

| Branch | Reviewed revision | Preserved contribution |
|---|---|---|
| `research-idea` | `01915001d9490914eb2f1a316c1ea06053adfaef` | Corpus mapping, clustering, source review, research proposal, V0 and pilot fact checking |
| `stage-b-development` | `f108a13eb6625fccc80bc5d57d435797519a1255` | Root writing workflow, contracts, diagnostics, revision and preservation |
| `sprint2-ui-demo` | `9c7fd63d9c53fb74912e678cc3bbb27b12bc5a50` | Streamlit UI, handover adapter, pinned backend, recorded runs and deployment records |
| `detector-half-2` | `061d3d2` | Detector, rewrite experiments, evaluation materials and detector-enhanced UI |

`detector-half-2` descends from the UI branch, which descends from the original writing branch. They are not four independent folders to concatenate. The integration branch restores Stage B content previously reverted on `main` and preserves the existing branch histories.

No existing branch was deleted. Uncommitted work in the original research checkout was not included, overwritten or treated as reviewed team code. Pushing or merging this local reorganisation is a separate review step.

## Moved files

| Previous location | Maintained location |
|---|---|
| `emnlp-literature/collect_emnlp.py` | `src/research/collect_emnlp.py` |
| `src/sample_papers.py` | `src/research/sample_papers.py` |
| `src/generate_ai_sections.py` | `src/research/generate_ai_sections.py` |
| `src/fact_checker.py` | `src/fact_checking/fact_checker.py` |
| `docs/part_a_research_development/*` | `docs/research/*` |
| `docs/cluster7_source_evidence_review.md` | `docs/research/cluster7_source_evidence_review.md` |

The three former `src/` script paths remain small compatibility launchers, not duplicate implementations. Repository-root calculations and the fact checker's draft path were updated for the new locations.

Research document bodies, evidence labels, source snapshots, detector outputs and saved model-run records are preserved. The old root writing README is retained as [writing workflow](writing_workflow.md), with its guide links and script locations updated.

The demo's pinned backend intentionally remains separate from the root backend until their differing feedback and reassessment behaviour can be consolidated and verified without losing work. See [architecture](architecture.md).
