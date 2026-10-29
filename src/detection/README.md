# AI-likeness detector, rewriting loop and human evaluation (Half 2)

All commands run from the repository root. Only `rewrite_loop.py` (live mode) calls an API.

| Step | Command | Output (results/detection/) |
|---|---|---|
| Train + validate detector | `python src/detection/train_detector.py` | `detector_model.json`, `detector_validation.json`, `feature_effects.csv` |
| Held-out test on real body text | `python src/detection/heldout_fulltext.py` | `heldout_fulltext.json` |
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

## Validation (honest numbers)

| Test | AUC |
|---|---|
| 5-fold CV, grouped by paper, all GPT paragraphs vs real abstracts | 0.74 |
| Like-for-like: 10 GPT abstracts vs real abstracts (small n) | 0.73 |
| **Held out: 344 passages of real body text from 18 papers it never saw** | **0.83** |
| TF-IDF baseline (not used) | 0.99 |

TF-IDF wins on paper because it learns topic and genre words. It gives the reviser no actionable feedback, and it would also flag any human paragraph whose topic is unusual.

## Known limitations

* The human reference is mostly abstracts. The held-out body-text test checks this, but PDF extraction is noisy.
* Generated text comes from one model (`gpt-5.6-luna`) and one prompt.
* Real 2025 papers may themselves be LLM-polished, which would make the reference less "human".
* A reviser optimising this detector can game it. That is why the human evaluation is the real test.
