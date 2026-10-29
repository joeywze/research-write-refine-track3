# Data and evidence inputs

| Folder/file | Purpose |
|---|---|
| `emnlp_2025_main.xlsx` | Original literature metadata corpus |
| `samples/` | Committed seeded pilot paper sample |
| `generated/` | Original pilot generated sections; exploratory writing data, not the approved research proposal |
| `processed/` | Cleaned corpus, clustering, embeddings, automated extraction and source-verification manifest |
| `facts/master_facts.xlsx` | Prepared evidence database used by the pilot matcher |
| `facts/pilot/` | Atomic draft claims and saved manual support assessments |
| `facts/evaluation/` | Existing claim-classification evaluation materials |
| `human_eval/` | Curated published-paper passages used by detector evaluation tooling |

The source review and proposal are in [docs/research](../docs/research/README.md). Old automated labels are retained separately from later source reviews; absence of a term in an abstract is not evidence that a paper did not study it.

The detector and interface depend on the current data paths, so they remain stable. Do not add credentials or identifiable participant responses here. Review paper-text redistribution permissions before publishing additional full-text material. Do not infer that every eligible paper or research topic is covered by this corpus.
