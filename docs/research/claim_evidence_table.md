# Cluster 7: claim-to-evidence table

Prepared 20 October 2026. This table follows Steps 1 and 2 of the research-development workflow.

Status definitions: **Supported by cited passage** means that the attributed statement is supported by the linked source text. It does not mean the reported experiment has been independently reproduced. **Unclear** means that the cited evidence does not establish the dimension. Boundaries below are reviewer interpretations, explicitly separated from author statements.

Every short excerpt below was checked against both the saved extraction and a fresh extraction from the local PDF. Page numbers are one-based PDF pages. Line wrapping is joined; no quoted wording is substantively rewritten.

## C01: Beyond the Surface: Measuring Self-Preference in LLM Judgments

Paper ID: [2025.emnlp-main.86](https://aclanthology.org/2025.emnlp-main.86/).

**Attributed claim:** The WMT19 judging prompt compares English translations of German text; the authors limit the task scope to instruction following and translation.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Judging prompt | "two different English translations of the same German text" | [Table 10, PDF p. 20](https://aclanthology.org/2025.emnlp-main.86.pdf#page=20) |
| Task-scope limitation | "this work limits its scope to instruction-following and translation tasks" | [Limitations, PDF p. 9](https://aclanthology.org/2025.emnlp-main.86.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English translation targets with German source text are explicit.

**Reviewer boundary, not an additional author claim:** Bilingual source/target material alone does not establish a matched comparison of judging responses in different languages.

## C02: Direct Judgement Preference Optimization

Paper ID: [2025.emnlp-main.103](https://aclanthology.org/2025.emnlp-main.103/).

**Attributed claim:** The authors state an English evaluation focus and identify multilingual judge development as future work.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Evaluation language | "our paper focuses on evaluation in English" | [Limitations, continued, PDF p. 10](https://aclanthology.org/2025.emnlp-main.103.pdf#page=10) |
| Future work | "future work is determining how to build judges for multilingual evaluation" | [Limitations, continued, PDF p. 10](https://aclanthology.org/2025.emnlp-main.103.pdf#page=10) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English evaluation focus is explicit.

**Reviewer boundary, not an additional author claim:** A limitation of this study is not evidence of absence across the literature.

## C03: From Generation to Judgment: Opportunities and Challenges of LLM-as-a-judge

Paper ID: [2025.emnlp-main.138](https://aclanthology.org/2025.emnlp-main.138/).

**Attributed claim:** This is a survey, and it discusses existing multilingual LLM-as-a-judge research.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Type of paper | "a comprehensive survey of the LLM-as-a-judge paradigm" | [Limitations, PDF p. 9](https://aclanthology.org/2025.emnlp-main.138.pdf#page=9) |
| Survey statement | "multilingual LLM-as-a-judge research has advanced with various methods and benchmarks" | [Appendix C.1.1, PDF p. 29](https://aclanthology.org/2025.emnlp-main.138.pdf#page=29) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Multilingual research is discussed; this excerpt is not an original experiment.

**Reviewer boundary, not an additional author claim:** Treat surveyed findings as leads to original studies; do not count them as experiments performed by the survey.

## C04: Arena-lite: Efficient and Reliable Large Language Model Evaluation via Tournament-Based Direct Comparisons

Paper ID: [2025.emnlp-main.360](https://aclanthology.org/2025.emnlp-main.360/).

**Attributed claim:** The stochastic experiment uses English-category Arena preferences; the limitations identify bracket-assignment randomness.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Stochastic experiment reference | "BT preferences from the English category of Chatbot Arena" | [Section 4.2, initial conditions, PDF p. 5](https://aclanthology.org/2025.emnlp-main.360.pdf#page=5) |
| Limitation | "variation due to initial match bracket assignments" | [Limitations, PDF p. 9](https://aclanthology.org/2025.emnlp-main.360.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English-category preferences are explicit for the cited setup.

**Reviewer boundary, not an additional author claim:** The English-category reference applies to the stated stochastic setup. Do not extend it to every experiment without further evidence.

## C05: Are Checklists Really Useful for Automatic Evaluation of Generative Tasks?

Paper ID: [2025.emnlp-main.538](https://aclanthology.org/2025.emnlp-main.538/).

**Attributed claim:** The authors identify an English-dataset limitation and report that checklists do not always improve evaluations.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Language/task limitation | "we utilize only a single English dataset for both the pairwise comparison and direct scoring tasks" | [Limitations, PDF p. 10](https://aclanthology.org/2025.emnlp-main.538.pdf#page=10) |
| Reported conclusion | "checklists do not always improve evaluations" | [Section 7, PDF p. 9](https://aclanthology.org/2025.emnlp-main.538.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English datasets are explicit for the two stated evaluation tasks.

**Reviewer boundary, not an additional author claim:** The checklist finding is not a measured cross-language effect.

## C06: Analyzing Uncertainty of LLM-as-a-Judge: Interval Evaluations with Conformal Prediction

Paper ID: [2025.emnlp-main.569](https://aclanthology.org/2025.emnlp-main.569/).

**Attributed claim:** The paper primarily analyses summarization and reasoning, includes a GenAI-Bench appendix experiment, and notes reliance on human calibration annotations.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Main task scope | "primarily analyze summarization and reasoning" | [Limitations, continued, PDF p. 10](https://aclanthology.org/2025.emnlp-main.569.pdf#page=10) |
| Appendix experiment | "we conduct experiments on GenAI-Bench" | [Appendix A.12, PDF p. 22](https://aclanthology.org/2025.emnlp-main.569.pdf#page=22) |
| Calibration caveat | "relies on high-quality human annotations for calibration" | [Ethical Considerations, PDF p. 10](https://aclanthology.org/2025.emnlp-main.569.pdf#page=10) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from these cited passages.

**Reviewer boundary, not an additional author claim:** Do not describe the paper as exclusively text-only: the appendix records an additional experiment. Test-language coverage remains unresolved here.

## C07: Meta-Rewarding Language Models: Self-Improving Alignment with LLM-as-a-Meta-Judge

Paper ID: [2025.emnlp-main.583](https://aclanthology.org/2025.emnlp-main.583/).

**Attributed claim:** The authors report persistent meta-judge positional bias as a limitation.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Remaining limitation | "Despite our efforts to mitigate positional bias of our meta-judge, this issue persists" | [Section 6, PDF p. 9](https://aclanthology.org/2025.emnlp-main.583.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from this cited passage.

**Reviewer boundary, not an additional author claim:** This is a limitation in the meta-rewarding setup, not a cross-language reliability result.

## C08: Self-Augmented Preference Alignment for Sycophancy Reduction in LLMs

Paper ID: [2025.emnlp-main.625](https://aclanthology.org/2025.emnlp-main.625/).

**Attributed claim:** The evaluated sycophancy tasks are Answer Suggestion and Are You Sure; the limitations explicitly restrict the study to English.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Evaluation tasks | "two sycophancy tasks: Answer Suggestion and Are You Sure." | [Section 3, PDF p. 4](https://aclanthology.org/2025.emnlp-main.625.pdf#page=4) |
| Language limitation | "this study focuses solely on the English language." | [Section 8, PDF p. 9](https://aclanthology.org/2025.emnlp-main.625.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English-only scope is explicit in the limitations; this resolves the earlier excerpt-level Unclear for this paper.

**Reviewer boundary, not an additional author claim:** The principal task is sycophancy assessment. Its use of an evaluator should not be conflated with a controlled multilingual judge study.

## C09: Improve LLM-as-a-Judge Ability as a General Ability

Paper ID: [2025.emnlp-main.712](https://aclanthology.org/2025.emnlp-main.712/).

**Attributed claim:** The study evaluates a judge on RewardBench using official English, basic Chinese and instructional Chinese prompt variants.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Judging-instruction variant | "Official English Prompt" | [Section 4.3.3, PDF p. 7](https://aclanthology.org/2025.emnlp-main.712.pdf#page=7) |
| Judging-instruction variant | "Basic Chinese Prompt" | [Section 4.3.3, PDF p. 7](https://aclanthology.org/2025.emnlp-main.712.pdf#page=7) |
| Judging-instruction variant | "Instructional Chinese Prompt" | [Section 4.3.3, PDF p. 7](https://aclanthology.org/2025.emnlp-main.712.pdf#page=7) |
| Evaluation benchmark | "evaluated the performance of the trained judge model on RewardBench" | [Section 4.3.3, PDF p. 7](https://aclanthology.org/2025.emnlp-main.712.pdf#page=7) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English and Chinese instruction variants are explicit; a matched response-language comparison is not established by this passage.

**Reviewer boundary, not an additional author claim:** Instruction-language variation and response-language variation are separate dimensions. These variants also differ in instruction detail.

## C10: Towards Optimal Evaluation Efficiency for Large Language Models

Paper ID: [2025.emnlp-main.716](https://aclanthology.org/2025.emnlp-main.716/).

**Attributed claim:** The experiment compares efficient subset-selection strategies and analyses reliability and semantic preservation.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Experiment design | "For a given compression rate, we performed efficient evaluations using different subset selection strategies and analyzed their reliability and semantic preservation." | [Section 4, PDF p. 3](https://aclanthology.org/2025.emnlp-main.716.pdf#page=3) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from this cited passage.

**Reviewer boundary, not an additional author claim:** Benchmark-subset reliability is a different construct from repeated LLM-judge agreement with human labels.

## C11: CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists

Paper ID: [2025.emnlp-main.796](https://aclanthology.org/2025.emnlp-main.796/).

**Attributed claim:** The authors focus on summarization and dialogue response generation and identify limits of binary evaluation questions.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Main task scope | "primarily focused on summarization and dialogue response generation" | [Section 9, PDF p. 10](https://aclanthology.org/2025.emnlp-main.796.pdf#page=10) |
| Binary-question limitation | "not all NLG tasks and evaluation criteria can be strictly answered with a yes/no response" | [Section 9, PDF p. 10](https://aclanthology.org/2025.emnlp-main.796.pdf#page=10) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from these cited passages.

**Reviewer boundary, not an additional author claim:** Do not infer language coverage from benchmark names alone. The proposed QA study below uses binary factual correctness, not a universal quality score.

## C12: Multi-perspective Analysis of Large Language Model Domain Specialization: An Experiment in Accounting Audit Procedures Generation

Paper ID: [2025.emnlp-main.891](https://aclanthology.org/2025.emnlp-main.891/).

**Attributed claim:** The main instruction specifies Japanese, and Appendix B records Portuguese and Chinese evaluation prompts and an English question-answer dataset.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Main-task instruction anchor | "in Japanese." | [Section 3.7, PDF p. 4](https://aclanthology.org/2025.emnlp-main.891.pdf#page=4) |
| MilkQA evaluation instruction | "Prompts for inference and evaluation were created in Portuguese." | [Appendix B.1, PDF p. 14](https://aclanthology.org/2025.emnlp-main.891.pdf#page=14) |
| cMedQA2 evaluation instruction | "Prompts for inference and evaluation were created in Chinese," | [Appendix B.2, PDF p. 14](https://aclanthology.org/2025.emnlp-main.891.pdf#page=14) |
| ELI5-Category description anchor | "English question-answer" | [Appendix B.3, PDF p. 14](https://aclanthology.org/2025.emnlp-main.891.pdf#page=14) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Japanese, Portuguese, Chinese and English are explicitly identified in the cited settings.

**Reviewer boundary, not an additional author claim:** The appendix changes datasets and domains. Multiple language settings alone do not establish a controlled paired language comparison.

## C13: Debatable Intelligence: Benchmarking LLM Judges via Debate Speech Evaluation

Paper ID: [2025.emnlp-main.953](https://aclanthology.org/2025.emnlp-main.953/).

**Attributed claim:** The experiments run multiple LLM judges on debate speeches and measure agreement with humans.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Evaluation design | "These experiments involve running multiple LLMs as judges on the speech dataset and measuring their agreement with humans." | [Section 4, PDF p. 3](https://aclanthology.org/2025.emnlp-main.953.pdf#page=3) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from this cited passage.

**Reviewer boundary, not an additional author claim:** This supports a human-agreement study in debate evaluation; multilingual coverage is not established by this passage.

## C14: Beyond the Score: Uncertainty-Calibrated LLMs for Automated Essay Assessment

Paper ID: [2025.emnlp-main.992](https://aclanthology.org/2025.emnlp-main.992/).

**Attributed claim:** The authors explicitly restrict the study to English and three public essay corpora.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Language/task scope | "This study is confined to English and to three public essay corpora" | [Limitations, PDF p. 5](https://aclanthology.org/2025.emnlp-main.992.pdf#page=5) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English is explicit.

**Reviewer boundary, not an additional author claim:** This is an essay-scoring scope limitation, not evidence that multilingual judging is unstudied elsewhere.

## C15: MR. Judge: Multimodal Reasoner as a Judge

Paper ID: [2025.emnlp-main.1021](https://aclanthology.org/2025.emnlp-main.1021/).

**Attributed claim:** MR. Judge formulates judgment as a reasoning-inspired multiple-choice problem and notes an evaluation-time cost.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Judge formulation | "we formulate the judgement process as a reasoning-inspired multiple-choice problem" | [Abstract, PDF p. 1](https://aclanthology.org/2025.emnlp-main.1021.pdf#page=1) |
| Limitation | "increases evaluation time" | [Section 9, PDF p. 9](https://aclanthology.org/2025.emnlp-main.1021.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from these cited passages.

**Reviewer boundary, not an additional author claim:** Multimodal content and multilingual evaluation are different dimensions.

## C16: Co-Eval: Augmenting LLM-based Evaluation with Machine Metrics

Paper ID: [2025.emnlp-main.1307](https://aclanthology.org/2025.emnlp-main.1307/).

**Attributed claim:** The translation experiment explicitly uses six target languages and the limitations mention metric-selection mismatches.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Translation experiment | "These models translate English content into six target languages: Chinese, Thai, Spanish, French, Ukrainian, and Vietnamese." | [Section 4.2, PDF p. 5](https://aclanthology.org/2025.emnlp-main.1307.pdf#page=5) |
| Retrieval limitation | "mismatches in metric selection" | [Limitations, PDF p. 9](https://aclanthology.org/2025.emnlp-main.1307.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Six target languages are explicit; resource-level classification is not established here.

**Reviewer boundary, not an additional author claim:** This is evidence that multilingual evaluation exists in the corpus. The quoted setup does not justify assigning universal language-resource categories.

## C17: Model Consistency as a Cheap yet Predictive Proxy for LLM Elo Scores

Paper ID: [2025.emnlp-main.1534](https://aclanthology.org/2025.emnlp-main.1534/).

**Attributed claim:** The authors state that the dataset human preference annotations were not used and identify difficulty distinguishing top-performing models.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Human-label use | "human preference annotations, these were not used in our study" | [Section 3.1, PDF p. 3](https://aclanthology.org/2025.emnlp-main.1534.pdf#page=3) |
| Limitation | "the metric lacks the ability to distinguish between top-performing models" | [Limitations, PDF p. 5](https://aclanthology.org/2025.emnlp-main.1534.pdf#page=5) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** Unclear from these cited passages.

**Reviewer boundary, not an additional author claim:** Separate unused item-level human labels from the paper's comparison with Arena Elo scores; do not label the work as having no human-derived reference of any kind.

## C18: Can Large Language Models Outperform Non-Experts in Poetry Evaluation? A Comparative Study Using the Consensual Assessment Technique

Paper ID: [2025.emnlp-main.1625](https://aclanthology.org/2025.emnlp-main.1625/).

**Attributed claim:** The study uses 90 English-language poems, includes repeated evaluations, and calls for direct expert validation.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Dataset scope | "limited to 90 English-language poems" | [Section 11, PDF p. 9](https://aclanthology.org/2025.emnlp-main.1625.pdf#page=9) |
| Repeated-run setting | "10 repeated evaluation runs of an LLM" | [Section 8, PDF p. 8](https://aclanthology.org/2025.emnlp-main.1625.pdf#page=8) |
| Validation limitation | "direct comparison against expert human judges for full validation" | [Section 11, PDF p. 9](https://aclanthology.org/2025.emnlp-main.1625.pdf#page=9) |

**Verification status:** Supported by cited passage; source wording checked.

**Language evidence:** English-language poems are explicit.

**Reviewer boundary, not an additional author claim:** Repeated-run reliability, performance against non-experts and validation by expert raters are distinct claims.
