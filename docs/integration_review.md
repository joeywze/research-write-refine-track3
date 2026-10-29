# Local integration and organisation review

Prepared 29 October 2026. This document records the local pre-publication review on `integrate-team-branches`. At that point the candidate had not been pushed, merged into `main` or deployed. Publication and integration are tracked in [pull request #6](https://github.com/joeywze/research-write-refine-track3/pull/6); consult that PR for its current merge state. The separate hosted application is not changed by this PR.

## Completed

- Combined the four source branches recorded in [contributions](contributions.md), retaining their Git ancestry.
- Restored the original writing functionality previously reverted on `main` before bringing in the UI and detector descendants.
- Created `src/research/`, `src/fact_checking/` and `docs/research/`; retained `src/writing/` and `src/detection/`.
- Updated moved-script repository roots and the fact checker's draft path. Kept three old script paths as compatibility launchers.
- Added the project README, architecture, evaluation, deployment and contribution guides, plus data/example/result indexes.
- Added missing fact-checker and PDF-extraction dependencies to root requirements.
- Preserved the Streamlit entrypoint, pinned backend, research snapshots, converted package/V0, detector outputs, model runs and support labels.
- Updated two UI test expectations for the detector branch's existing wording/help panels, without changing UI behaviour.
- Made an existing Windows-only launcher test check the equivalent Windows and POSIX process-isolation behaviour.
- Added layout, provenance, compatibility-launcher and offline detector-screen regression tests, and added demo/interface suites to CI.

## Offline results

| Suite | Result |
|---|---|
| Root writing and repository-layout checks | 63 passed |
| Pinned demo writing backend | 68 passed |
| Demo integration, upload, citation and launcher checks | 31 passed |
| Handover and preserved-content checks | 10 passed |
| Streamlit interface, research records and detector checks | 23 passed |
| Synthetic package and matching six-section V0 | Valid; semantic grounding not checked |

Total: **195 passing tests**. These suites were run locally with Python 3.12 and the demo dependencies. They use fixtures, recorded inputs or mocked model providers. They are not a live deployment check, a new fact-checking study or proof of model quality.

The detector UI emits existing pandas deprecation and mixed-type Arrow-conversion warnings under the test environment; Streamlit applies its fallback conversion and the interface tests pass. Those warnings are not reported here as application crashes.

## Not performed during the local review

- No paid model call, corpus recollection, detector retraining or replacement of recorded results.
- No new human approval, novelty sign-off, independent ratings or reclassification of the four flagged pilot claims.
- No deletion of a team branch or uncommitted research-checkout work.
- No push, pull request, `main` update or hosted deployment.

## Release checklist recorded at local review

1. Review the file moves, README, ownership attribution and retained historical outputs.
2. Agree a reviewed commit with the deployment owner. The separate hosted repository is not updated automatically.
3. Confirm how to manage new private answer keys and human responses. The already tracked historical key is public, not made private by this cleanup.
4. Consolidate the two differing writing backends only as a separately tested change; neither is discarded here.
5. Obtain approval to publish the candidate and integrate through a pull request. The user subsequently authorised the push and merge; see PR #6 for the integration record.
