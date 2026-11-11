# AI-likeness detector, rewriting loop and human evaluation (Half 2)

Run the commands from the repository root. The live rewriting scripts call an API.
For a follow-up edit of an accepted Stage B draft, use the [optional review pass](../../docs/writing_workflow.md#optional-review-of-accepted-v2). The historical full-paper experiment starts from V0 and uses its own mechanical checks.

| Step | Command | Output (results/detection/) |
|---|---|---|
| Train + validate detector | `python src/detection/train_detector.py` | `detector_model.json`, `detector_validation.json`, `feature_effects.csv` |
| Historical body-text comparison | `python src/detection/heldout_fulltext.py` | `heldout_fulltext.json` |
| Score saved Stage B runs | `python src/detection/score_runs.py` | `run_scores.csv`, `paragraph_scores.csv` |
| Validation chart | `python src/detection/plot_validation.py` | `detector_validation.png` |
| Score any text | `python src/detection/detector.py --file draft.md` | printed breakdown + flagged sentences |
| Rewriting loop (naive vs guided) | `python src/detection/rewrite_loop.py --n 10 --iters 4` | `loop_log.csv`, `loop_curve.png`, `loop_examples.md` |
| Human eval form | `python src/detection/human_eval.py build` | `human_eval/form_for_raters.md`, `PRIVATE_answer_key.csv` |
| Human eval scoring | `python src/detection/human_eval.py score responses.csv` | `human_eval/human_eval_results.csv` |

`data/processed/cluster7_fulltext_evidence.csv` is copied from the `research-idea` branch.

## Why this detector

The track asks how AI-sounding a draft is. The Stage B rules and critic measure review points, not that, and the rules scored the real draft 0 before any revision. So the score had nowhere to fall.

* **Data:** 1,808 real EMNLP 2025 abstracts (human) versus 386 GPT paragraphs from the pilot corpus (AI).
* **Features:** 18 stylometric features covering each symptom in the brief.
  * Each is standardised against the real-paper distribution.
  * A logistic regression combines them, constrained so every weight points in its expected direction (for example, more hedging can only mean more AI-like).
  * Without that constraint the model learns that real abstracts use "robust" and "significant" more than GPT, and the rewriting loop would then reward clichés.
* **Excluded on purpose:**
  * Numbers and citations: the generator was told not to invent them, so a reviser optimising them would be pushed to fabricate.
  * First-person "we": real abstracts nearly always use it but related-work paragraphs don't, so it measures genre, not style.
* **What it ended up using:** hedge density, stock phrases, lists of three, too few long sentences, and too-uniform sentence lengths. The lexicon features ("delve", "crucial", promotional adjectives) got zero weight because real EMNLP abstracts use them *more* than our generator did.

## Recorded detector experiments

The all-10-papers row is the number to report; the fixed split confirms it. Reproduce it with the commands in `make_holdout_split.py`; the results are copied to `results/detection/heldout_eval/`.

| Test | AUC |
|---|---|
| 5-fold CV with separate human and generated groups, GPT paragraphs vs real abstracts | 0.74 |
| Like-for-like: 10 GPT abstracts vs real abstracts (small n) | 0.73 |
| Body-text comparison, 344 passages from 18 papers represented in training by their abstracts | 0.83 |
| TF-IDF baseline (not used) | 0.99 |
| **Unseen papers, all 10 AI papers** (paper-grouped 5-fold CV, `make_holdout_split.py cv`) | **0.74** (95% interval by paper 0.72-0.76; single papers 0.67-0.81) |
| Unseen papers, one fixed split (`make_holdout_split.py`, seed 17): 3 AI papers (118 paragraphs) + 153 real abstracts, detector retrained without them | 0.76 (accuracy at 50: 70%); its 3 held-out papers happen to be among the easier ones |

TF-IDF wins on paper because it learns topic and genre words. It gives the reviser no actionable feedback, and it would also flag any human paragraph whose topic is unusual.

The body-text comparison uses the final fitted detector for the human passages and out-of-fold predictions for generated text. Treat it as a comparison across text types. For an unseen-paper evaluation, split by the underlying paper ID across both classes and all versions before fitting, then use the same frozen detector for both held-out classes.

## Evaluate a new paper split

Before fitting, record the held-out paper IDs in a JSON array. Use the same source ID for real passages, generated passages and every revision of the same paper. Prepare separate human and generated CSV files with `paper_id` and `text` columns. Match sections and passage lengths where possible, and use papers the team has not inspected or used to tune its prompts or detector.

```text
python src/detection/train_detector.py --holdout evaluation-output/paper_ids.json --output evaluation-output/detector
python src/detection/evaluate_holdout.py --model evaluation-output/detector/detector_model.json --human evaluation-output/human.csv --generated evaluation-output/generated.csv --output evaluation-output/holdout
```

Training excludes the listed papers from both classes. Each training paper has one cross-validation fold across all of its rows. Evaluation requires the recorded held-out IDs and rejects any overlap with training papers. Both classes use the same fitted model. The output records the model and input hashes, sample counts and passage-level AUC. AUC measures separation between the two text groups. Compare writing quality and preservation separately with human reviewers.

## Known limitations

* The human reference is mostly abstracts. The held-out body-text test checks this, but PDF extraction is noisy.
* Generated text comes from one model (`gpt-5.6-luna`) and one prompt.
* Real 2025 papers may themselves be LLM-polished, which would make the reference less "human".
* A reviser optimising this detector can game it. That is why the human evaluation is the real test.

## Which script to use (Sprint 3)

| Purpose | Use |
|---|---|
| Revise a draft with all checks | `sprint2_demo/half2_pipeline.py` (detector + reviewer + rewriter + checks) |
| Test the checks against known errors | `sprint2_demo/seeded_faults.py` |
| Detector on unseen papers | `make_holdout_split.py` (+ Guan Hong's `train_detector.py --holdout`, `evaluate_holdout.py`) |
| External check with GPTZero | `gptzero_check.py` |
| Sprint 2 experiments, kept so reported numbers can be reproduced | `rewrite_loop.py` (helpers still used), `revise_full_paper.py`, `heldout_fulltext.py`, `score_runs.py` |

