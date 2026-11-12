# Human or AI? (study 3)

For each passage, choose: written by a person, or written by AI. Then rate your confidence (1-5).

## Item 01

A model can appear safe by refusing nearly everything. It can also appear helpful by answering requests that should have been refused. A valid safety evaluation must therefore measure unsafe compliance on harmful inputs and false refusal on benign inputs. In multilingual settings, a translated or code-switched prompt can alter intent, severity, or local meaning.

## Item 02

Consequently, we use token probabilities as input. However, token probabilities are well known to have multicollinearity, which makes them unsuitable for regression-based approaches. Thus, we only use token probabilities as the input for ordinal classification-based approaches, while use token logits directly for regression-based approaches. Boundary Adjustment Due to the ordinal and discrete nature of ratings, a continuous interval whose upper and lower bounds are continuous numeric values might not have exact meaning.

## Item 03

Training text embedding models under differential privacy constraints is challenging due to the high dimensionality of language data and the presence of rare, identifying linguistic features. We propose (Differentially Private Embedding Distillation), a framework that leverages teacher-student distillation with multi-layer noise injection to learn high-quality embeddings while providing differential privacy guarantees.

## Item 04

Agreement with human judgments, consistency across languages, and stability across repeated calls describe different aspects of an automated evaluator. A judge may produce stable decisions that are nevertheless incorrect, or agree with humans in one language but not on a meaning-matched version in another. We propose a controlled bilingual study that measures these properties separately in context-grounded short question answering.

## Item 05

The planned pilot contains 20 underlying passage–question items. Each item will have a correct answer and a minimally altered incorrect answer in both languages, yielding 80 response texts before exclusions. Incorrect variants will change a substantive entity, quantity, or relation while keeping the answer form as similar as practical. Human review will verify that a variant is actually incorrect, not an alternative valid expression.

## Item 06

Cross-modal retrieval is essential for interpreting cultural heritage data, but its effectiveness is often limited by incomplete or inconsistent textual descriptions, caused by historical data loss and the high cost of expert annotation. While large language models (LLMs) offer a promising solution by enriching textual descriptions, their outputs frequently suffer from hallucinations or miss visually grounded details.

## Item 07

Natural-language explanations are useful only if their apparent reasons bear a defensible relationship to the model decision. A fluent explanation can look plausible to a reader and still be post-hoc, incomplete, or behaviorally irrelevant. One remedy is iterative refinement: generate an explanation, critique it, then revise it until a faithfulness score improves.

## Item 08

Conventional speculative decoding (SD) methods utilize a predefined length policy for proposing drafts, which implies the premise that the target model smoothly accepts the proposed draft tokens. However, reality deviates from this assumption: the oracle draft length varies significantly, and the fixed-length policy hardly satisfies such a requirement. Moreover, such discrepancy is further exacerbated in scenarios involving complex reasoning and long-form generation, particularly under test-time scaling for reasoning-specialized models.

## Item 09

The design is limited to one selected language pair, one primary judge, a small sample, and constructed short-answer errors. It cannot establish broad multilingual fairness or deployment safety, and it does not support claims about performance across model families. Minimal errors can be too easy or unrepresentative of naturally generated answers.

## Item 10

Hallucination detectors are intended to respond to factual error or lack of source support, yet their scores vary with answer length, lexical overlap, and phrasing. Existing research already identifies label misalignment, domain shift, response-length effects, and detector-family blind spots. The gap is not another broad robustness benchmark. It is a paired form-invariance audit that holds factual status and evidence fixed.

## Item 11

Video large language models (Vid-LLMs), which excel in diverse video-language tasks, can be effectively constructed by adapting image-pretrained vision-language models (VLMs). However, this adaptation remains challenging, as it requires processing dense and temporally extended visual inputs that exceed the capacity of image-based models. This paper identifies the perception bottleneck and token overload as key challenges in extending image-based VLMs to the video domain.

## Item 12

For example, evaluators are typically asked to rate text on a Likert scale from 1 to 5 (higher is better) on dimensions such as coherence, consistency, fluency, and relevance. While Likert scales are useful for capturing ordinal relationships in human evaluation, they face two key challenges when applied to LLM-based evaluator models.

## Item 13

Our experiments yield three key findings: First, we observe that the effectiveness of selective checklist application varies by task; in some cases, it achieves comparable or better correlations than full application, while in others it does not. This suggests that checklist use is not universally beneficial. Second, our analysis reveals that the most useful checklist creation method varies across different evaluation models and tasks, suggesting that no single approach works best in all settings.

## Item 14

Large language models (LLMs) have made significant breakthroughs in extracting useful information from conversation history to enhance the response in long-term conversations. Summarizing useful information from historical conversations has achieved remarkable performance, which, however, may introduce irrelevant or redundant information, making it difficult to flexibly choose and integrate key information from different sessions during memory retrieval.

## Item 15

Versions, settings, and preprocessing will be frozen together. Thresholds will be chosen using separate calibration data that do not share briefs or revision histories with the test set. Raw scores will remain the primary output, and binary rates will be threshold-dependent secondary summaries. Invalid, truncated, and unsupported inputs will be reported as failures.

## Item 16

AGSER uses attention-guided self-reflection and response consistency without task-specific training samples, but its failure analysis includes difficulty with query segmentation. IRIS derives features from truth-verification behavior and internal representations; its reported scope is bounded to single statements. These methods motivate including reflection and representation families. We do not assume that every detector is a surface classifier.

## Item 17

These values are particularly noteworthy as they exceed the typical thresholds of 0.7 to 0.9 that are often considered acceptable for panels of human judges in CAT studies. These high scores suggest that the forced-choice methodology is a reliable driver of the models’ strong performance. By compelling the LLMs to make nuanced, relative judgments rather than absolute ones, our method enhances their ability to consistently differentiate between the ground-truth quality tiers, resulting in a stable and reproducible assessment tool.

## Item 18

The core sample contains 480 item–model cells, drawn from two tasks, two models, and 120 eligible items for each task–model pair. Five explanation conditions span two revision depths; intervention controls and repeats add to the inference workload. Before the frozen test set is fixed, a 20-item-per-cell pilot will validate parsing, metric execution, and cost.

## Item 19

“Human-written” and “AI-written” are often treated as mutually exclusive properties of a final document. Real revision workflows violate that assumption. A human drafts a text and asks a model to reorganize it; a model produces a first draft that a person rewrites; different sentences can have different origins. Without a declared target, a detector score could be interpreted as evidence about the initial drafter, the latest editor, the current wording, or simply a stylistic resemblance to its training data.

## Item 20

(2) DPO Enhancement: For questions where GPT-4o fails to provide accurate labels, we sample responses from the SFT-trained model and partition them into chosen and rejected pairs based on ground-truth preferences. These pairs are then used for DPO to refine the model’s preferences. This two-stage approach simplifies the judge task into two subtasks, style adaptation and accurate analysis, significantly reducing the data and computational resources required for training.
