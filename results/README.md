# Results index

Existing outputs are retained in place because the interface reads these paths. This cleanup labels their purpose rather than deleting or recomputing teammates' results.

| Location | Contents | Interpretation |
|---|---|---|
| `fact_checking/draft_v0_evidence_matches.csv` | Ranked evidence matches for pilot draft claims | Textual relevance, not a new semantic verdict |
| `detection/detector_model.json` | Saved detector parameters | Used by the interface's local scorer |
| `detection/detector_validation.*` | Recorded detector validation report and figure | Development experiment; see detector limitations |
| `detection/heldout_fulltext*` | Recorded held-out experiment and passage inputs | Check the source split and design before generalising |
| `detection/run_scores.csv`, `paragraph_scores.csv` | Scores for saved writing versions | Different from the writing critic's issue counts |
| `detection/loop_*` | Recorded rewriting experiments | Inspect condition, guard status and dry-run suffixes |
| `detection/*_dryrun*`, `detection/full_paper_dryrun/` | Dry-run artifacts | Not live model performance |
| `detection/*_v1_unguarded*` | Earlier unguarded-loop records | Historical comparison, not the guarded final method |
| `detection/full_paper/` | Detector-guided paper experiment | `final_paper_v3.md` is not research-team sign-off |
| `detection/human_eval/` | Historical form, response template and answer key | Form preparation is not completed human ratings; the tracked key is public |
| `../sprint2_demo/runs/live-*` | Recorded real-model writing runs, including rejected attempts | Development observations for the pinned package |

The deliberate study-detail change exercise is a controlled safety test, not an observed spontaneous model error. Newly generated safety records and local job records belong under the demo's ignored verification paths.

Do not overwrite recorded files just to rerun checks. Use fresh output locations and preserve the input revision, configuration and whether the run was live, mocked, dry-run or deliberate. No new experiment was run to produce the organisation guides.

See [evaluation](../docs/evaluation.md) for metrics, software tests, private evaluation handling and remaining independent validation.
