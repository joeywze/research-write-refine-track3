# Architecture and handover

## Components

| Component | Location | Responsibility |
|---|---|---|
| Research scripts | `src/research/` | Corpus collection, sampling and separate pilot section generation |
| Exploratory analysis | `notebooks/` | Corpus mapping, clustering and AI-assisted literature analysis |
| Research documentation | `docs/research/` | Reviewed quotations, interpretation boundaries, candidate gap, study proposal and V0 |
| Fact checking | `src/fact_checking/` | Pilot claim classification, evidence retrieval and reporting saved support labels |
| Writing | `src/writing/` | Root command-line writing review, revision and preservation pipeline |
| Detection | `src/detection/` | AI-likeness detector, rewrite experiments and human-evaluation tooling |
| Streamlit demo | `sprint2_demo/ui/app.py` | Research, Draft, Refine, Results and Detect views |

## Current handover

Research preparation runs before the demo. The adapter in `sprint2_demo/handover.py` converts the pinned proposal into schema 0.1 `research_package.json` and matching `v0.json`. This adapter uses explicit mappings for the existing case study; it is not a general proposal-generation pipeline.

The package records the question, gap, contribution, proposed methodology, sources, evidence, claims, qualifications, limitations and unknowns. The draft maps paragraphs to claims and citations. Structured input validation is not source verification or research-team approval.

## Maintained documents versus frozen snapshots

- The editable research proposal and evidence documents now live under `docs/research/`.
- `sprint2_demo/inputs/source/` preserves the original reviewed source snapshot.
- `sprint2_demo/inputs/source_manifest.json` records paths and Git blob hashes at the original research revision. Those historical paths must not be rewritten to make the new layout appear original.
- `sprint2_demo/inputs/converted/` is the real, prepared handover consumed by the demo.
- Root `examples/` and `sprint2_demo/backend/examples/` are synthetic test fixtures.

Updating the editable proposal must not silently overwrite the snapshots or recorded run hashes. A new source revision needs an explicit reviewed conversion and a new run.

## Why two writing backends remain

The demo loads `sprint2_demo/backend/src/writing/`; the root command-line interface loads `src/writing/`. They are not identical: the demo copy includes accountable feedback and stable reassessment of unchanged paragraphs.

Both implementations and their tests are preserved. Consolidating them requires comparing behaviour and running both suites; this reorganisation does not discard either implementation. Do not add a root `src/__init__.py` casually: the demo currently uses namespace-package resolution to load its pinned backend.

## Safety boundaries

Research-package approval is pending for the prepared case study. The writing loop can run a provisional development example with explicit controls; it does not create human approval. The source-support warnings remain visible.

The hosted preview disables paid inference. The local live launcher passes credentials only to the server/worker environment and uses the existing budget and concurrency guards. Detector scoring in the interface is local and distinct from either fresh model inference or evidence checking.

Reusable paper selection, AI-generated candidate directions and human-approved package export remain planned work.
