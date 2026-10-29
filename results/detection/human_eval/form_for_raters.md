# Real or generated?

Each paragraph below is either from a published EMNLP 2025 paper or was generated with an LLM for our project. All are about evaluating LLMs as judges; citations were removed from all of them. For each one choose **Real paper** or **Generated**, and how confident you are (1 = guess, 5 = certain). Optional: one phrase that gave it away.

## Item 01

With 20 qualifying items, there will be 40 candidate responses per content language. Each of the three conditions requires 40 responses × 3 calls, giving 360 scheduled J1 calls. Initial human annotation requires 80 response texts × 2 ratings, or 160 ratings. Translation review, practice, adjudication and any technical retries add workload. An optional J2 would require another 360 calls.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 02

These values are particularly noteworthy as they exceed the typical thresholds of 0.7 to 0.9 that are often considered acceptable for panels of human judges in CAT studies. These high scores suggest that the forced-choice methodology is a reliable driver of the models’ strong performance. By compelling the LLMs to make nuanced, relative judgments rather than absolute ones, our method enhances their ability to consistently differentiate between the ground-truth quality tiers, resulting in a stable and reproducible assessment tool. Looking forward, the success of this CAT-inspired framework suggests it is a promising and durable approach for automated creative assessment. As LLM capabilities continue to evolve, a critical next step will be to determine if this methodology can enable them to match the evaluations of domain experts, moving beyond the non-expert benchmark surpassed here.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 03

Improving the judging capabilities of smaller models remains an important goal, as this would expand accessibility and reduce the computational cost of deploying LLM-as-a-Judge systems. Beyond model size, further research is needed to better align LLM judgment behavior with human evaluations, particularly in capturing nuanced patterns and system-level preferences. Another promising direction is to explore multidimensional evaluations, where judges provide separate ratings for aspects such as rhetorical style, coherence, factual grounding, and persuasiveness, complementing the holistic score.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 04

An English-focused study can motivate extending that study without establishing an absence elsewhere. For example, Wang et al. explicitly limit their evaluation to English and identify multilingual judging as future work. Conversely, Wu et al. examine translation evaluation across six target languages. The relevant comparison is therefore between specific tasks and evaluation protocols, rather than English-only and multilingual research as mutually exclusive categories.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 05

We propose a controlled bilingual QA study that evaluates human–judge agreement, cross-language decision changes and repeated-call stability as distinct outcomes. Matched correct and incorrect candidates, human review in each language and a separate instruction-language contrast make the intended comparisons explicit. The contribution is a bounded, auditable replication-and-extension design. The evaluation plan does not presume a language disadvantage or an improvement from translated instructions; its purpose is to determine which conclusions the selected data and protocol can support. Experimental performance remains to be measured.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 06

The planned pilot contains 20 underlying passage–question items. Each item will have a correct answer and a minimally altered incorrect answer in both languages, yielding 80 response texts before exclusions. Incorrect variants will change a substantive entity, quantity or relation while keeping the answer form as similar as practical. Human review will verify that a variant is actually incorrect rather than an alternative valid expression.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 07

Consequently, it is imperative to also improve the model’s capabilities as a judge in addition to its ability to act. In this paper, we propose a novel method called Meta-Rewarding which assigns rewards to its own judgements to train the model’s ability to judge. The key idea is to introduce a third role of meta-judge, whose task is to evaluate the model’s own judgements. While the judge evaluates the actor’s responses, the meta-judge evaluates the judge’s judgments (including rewards that it assigns) using a mechanism similar to LLM-as-a-Judge, which we term LLM-as-a-Meta-Judge. The meta-judge enables us to build training data containing preference pairs of judgements, in addition to the standard preferences between actor responses derived from the standard judge.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 08

To separate these mechanisms, we will also report binary decision coverage, agreement conditional on a valid binary decision, and rates of abstention, invalid output and technical failure. Conditional Cohen's kappa will be reported beside coverage; it will be marked undefined when its denominator is zero. The primary paired contrast is agreement in B minus agreement in A. A contrast caused by technical failures will be described as an operational difference, not automatically a language-understanding deficit.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 09

The absolute QWK numbers on FCE are markedly lower than on TOEFL11, even though both datasets use the same low/medium/high mapping. Two factors help to explain the gap. First, the FCE essays are mapped post-hoc from a 40-point holistic scale, and quadratic penalises any band disagreement proportionally to the original distance on that underlying scale; a one-band slip therefore receives a much heavier penalty than in TOEFL11, whose native rubric already has three discrete labels. Second, the FCE corpus is almost one order of magnitude smaller than TOEFL11, magnifying the impact of label noise and leaving less data for both fine-tuning and calibration.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 10

Our experiments yield three key findings: First, we observe that the effectiveness of selective checklist application varies by task; in some cases, it achieves comparable or better correlations than full application, while in others it does not. This suggests that checklist use is not universally beneficial. Second, our analysis reveals that the most useful checklist creation method varies across different evaluation models and tasks, suggesting that no single approach works best in all settings. Third, our analysis shows that many checklist items, although useless for improving human correlation, still overlap substantially with human-written items. This suggests that inconsistencies may stem from the subjective nature of human evaluations and underscores the need to rethink the objective criteria we expect from responses.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 11

Cross-language decision changes will be assessed between conditions A and B for the same item, answer variant and repeat index. The change rate will be calculated where both outputs are binary decisions, with paired coverage and non-decision mismatches reported. Repeat-index matching defines this pilot's descriptive comparison; it does not make the two calls shared random draws or independent item samples. For RQ3, the same agreement and stability measures will compare C with B.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________

## Item 12

Some perform significantly better or worse than expected given their parameter count. Therefore, there is a need for a method to independently evaluate models. The current best way to evaluate a model is to measure its Elo score by comparing it to other models in a series of contests—an expensive operation since humans are ideally required to compare LLM outputs. We observe that when an LLM is asked to judge such contests, the consistency with which it selects a model as the best in a matchup produces a metric that is 91% correlated with its own human-produced Elo score. This provides a simple proxy for Elo scores that can be computed cheaply, without any human data or prior knowledge.

- [ ] Real paper   - [ ] Generated   Confidence 1-5: ___   Tell: ________
