# Cluster 18: external evidence and counterevidence

Prepared 5 November 2026. These 5 close 2026 papers were selected because they could invalidate or materially narrow the proposed gap. Their full PDFs were reviewed, not only their abstracts. Each record includes two passages verified against the original PDF.

## E01: Please refuse to answer me! Mitigating Over-Refusal in Large Language Models via Adaptive Contrastive Decoding

Paper ID: [2026.acl-long.1823](https://aclanthology.org/2026.acl-long.1823/).

**Problem and method.** The authors investigate how to reduce inappropriate refusals of harmless queries without weakening refusals of malicious queries. They argue that fixed contrastive decoding policies suppress or reinforce refusal indiscriminately, creating a safety–helpfulness trade-off, and ask whether token-level adaptive switching can improve both outcomes. Adaptive Contrastive Decoding (AdaCD) contrasts the same model with and without the extreme system prompt “Please refuse to answer me!” to extract a refusal-oriented token distribution. An agreement measure based on the prompted top token’s rank in the unprompted distribution, together with a confidence constraint, determines whether to add or subtract that distribution.

**Data and experiment.** Benign over-refusal evaluation uses XSTest-Safe, ORBench and OKTest; malicious-query evaluation uses XSTest-UnSafe, AdvBench and JailBench. Just Eval supplies open-ended usability tasks, including coding. Evaluation relies on benchmark safe/malicious partitions rather than a newly developed harm-label taxonomy. The paper provides English prompts and examples but does not report language- or register-stratified evaluation or native-speaker review. Experiments compare Llama3-8B-Instruct, Gemma2-9B-It and Qwen3-8B using Default, Prompt, SSD, Surgical, SelfCD and AdaCD; Qwen3 thinking is disabled, with greedy decoding and a 512-token maximum. SSD expert models for Gemma2 and Qwen3 were fine-tuned by the authors because corresponding released experts were unavailable. WildGuard supplies primary refusal/safety judgments; GPT-4 provides usability scores and a secondary Qwen3 evaluation on XSTest partitions.

**Author-stated limitation reviewed.** PDF page 9: Fixed λ and α settings may be improved by adapting them to individual user queries.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Extreme refusal prompt | “Please refuse to answer me!” | [3.1 Key Observations and Insights; PDF p. 4](https://aclanthology.org/2026.acl-long.1823.pdf#page=4) |
| Evaluation limitation | “We did not conduct human evaluations or keyword-based evaluations” | [6 Limitations; PDF p. 9](https://aclanthology.org/2026.acl-long.1823.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Shows the safety-helpfulness trade-off is already an explicit mitigation target.

## E02: Multilingual Refusal Alignment for Safer Large Language Models

Paper ID: [2026.findings-acl.1537](https://aclanthology.org/2026.findings-acl.1537/).

**Problem and method.** The authors investigate whether refusal alignment learned in one language transfers to others, whether multilingual alignment preserves responses in the user's language, and how safety training affects multilingual capabilities. Their central concern is that English safety performance alone may conceal unsafe behavior or language switching elsewhere. The authors construct RefusEU using synthetic adversarial questions, preferred refusal responses from Llama-3.1-70B, and dispreferred responses from an abliterated variant. Llama-Guard-3-8B and PolyGuard-Qwen filter prompts and response pairs, while FastText filters language mismatches. They apply DPO to externally released, already-abliterated Llama-3.1 8B and 70B models, comparing multilingual and single-language training.

**Data and experiment.** RefusEU covers English, German, Italian, French, Spanish, Portuguese, Polish, Czech, Slovak, Slovenian, Lithuanian, and Latvian. Its 14 Llama-Guard hazard categories span violence, nonviolent crime, sexual harms, defamation, specialized advice, privacy, intellectual property, weapons, hate, self-harm, sexual content, elections, and code-interpreter abuse. The four DPO conditions use balanced 12-language data, six high-resource languages, English alone, or all languages except English; their training sizes differ. Eleven additional non-English single-language runs use the 8B model. Comparisons include abliterated and original instruction-tuned Llama baselines, Qwen2.5 7B/14B, Mistral Small 24B, Mistral Nemo, and gpt-oss-20B. Safety labels come from two guards with GPT-4o-mini adjudicating disagreements.

**Author-stated limitation reviewed.** PDF page 9: RefusEU covers only 12 of the 24 official European languages, and the authors call for broader language coverage.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Refusal-only preference target | “the chosen answer for unsafe prompts is always a refusal.” | [3 Dataset construction; PDF p. 4](https://aclanthology.org/2026.findings-acl.1537.pdf#page=4) |
| Translated rather than native-language human audit | “Samples were machine translated to English” | [C.2 Manual review; PDF p. 17](https://aclanthology.org/2026.findings-acl.1537.pdf#page=17) |

**Effect on candidate gap - reviewer interpretation.** Further constrains any broad multilingual-safety novelty claim and supports a setting-bounded replication framing.

## E03: Register Shifts Break LLM Safety: A Bengali Benchmark with Culturally Grounded Harms

Paper ID: [2026.findings-emnlp.1403](https://aclanthology.org/2026.findings-emnlp.1403/).

**Problem and method.** The authors investigate whether everyday Bengali register and authority framing alter LLM compliance with culturally grounded harmful requests. They argue that translation-based evaluation can miss Bangladesh-specific harm terminology and sociolinguistic variation, and examine whether existing safety evaluators reliably classify the resulting responses. BANGLA SAFE combines native prompt authorship with Claude Opus 4.7-assisted generation and line-by-line native-speaker review. Harm-act schemas are rendered in English direct, English institutional, formal Bengali journalism, colloquial code-mixed Bengali, and Bengali institutional conditions. Responses receive REFUSE, POLICY, PARTIAL, or HARMFUL labels from a human-validated Claude judge; loose ASR combines PARTIAL and HARMFUL, whereas strict ASR counts only HARMFUL.

**Data and experiment.** The dataset contains 879 total condition-specific prompts, not 879 prompts per condition: 309 human-authored and 570 synthetic, including 338 English, 190 colloquial Banglish, and 351 Bengali-script prompts. The authors query 18 models at temperature 0, top-p 1, without system prompts, producing 15,822 responses. Models include Llama-3.2-3B, Llama-3.1-8B, Llama-3.3-70B, Qwen3-8B/30B, TigerLLM-1B/9B-it, Gemma-3-12B/27B, Gemma-4-26B, DeepSeek-V3/V4-Pro, Claude-Haiku-4.5, GPT-4.1-mini, GPT-5-mini, Gemini-2.5-Flash, Grok-4.3, and Mistral-Medium-3.

**Author-stated limitation reviewed.** PDF page 9: The lexical coverage probe of twelve open safety corpora does not establish causality for observed ASR differences.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Native review of synthetic prompts | “Each generated prompt was reviewed line-by-line by native Bangla-speaking annotators” | [3.3 Prompt Construction; PDF p. 5](https://aclanthology.org/2026.findings-emnlp.1403.pdf#page=5) |
| Benign coverage limitation | “does not include a benign control set” | [Limitations; PDF p. 9](https://aclanthology.org/2026.findings-emnlp.1403.pdf#page=9) |

**Effect on candidate gap - reviewer interpretation.** Demonstrates native/expert culturally grounded harmful-prompt review but lacks the matched benign control central to this proposal.

## E04: Does Safety Live in a Shared Multilingual Subspace? Cross-Lingual (Non-)Transfer of the Refusal Direction

Paper ID: [2026.mrl-1.19](https://aclanthology.org/2026.mrl-1.19/).

**Problem and method.** The authors investigate whether multilingual refusal is mediated by a shared linear residual-stream direction or language-specific mechanisms. They distinguish cross-language geometric alignment from causal transfer of English-derived interventions, motivated by lower harmful-request refusal rates outside English and the implications for multilingual safety evaluation. For each language and layer, the authors estimate a difference-in-means direction between unsafe and benign prompt activations at the final prompt token. They compare cross-language cosine alignment with a matched non-safety task contrast, using reliability correction, sample-size matching and logistic-probe robustness checks. Causal tests remove the English direction at every layer and token on unsafe prompts or add it at a selected layer on benign prompts, comparing effects with each language's own direction.

**Data and experiment.** The study uses 315 released, human-translated MultiJail unsafe prompts and 100 corresponding machine-translated Aya/Dolly benign instructions per language, totaling 4,150 prompt-language instances. Languages are English; Chinese, Italian and Vietnamese; Arabic, Korean and Thai; and Bengali, Swahili and Javanese, grouped by MultiJail resource tiers. Models are Qwen2.5-7B-Instruct in 4-bit NF4 and Llama-3.2-3B-Instruct in bf16; a pre-registered Aya-Expanse-8B run did not complete. Baseline refusal, English-direction interventions, within-language-direction interventions and matched non-safety geometry are compared. The layer of record maximizes held-out English projection AUROC; additional layers are reported separately after this selection proved insensitive to causal mediation.

**Author-stated limitation reviewed.** PDF pages 5–6: Unsafe prompts are human-translated whereas benign prompts are machine-translated, so their difference-in-means may absorb translationese.

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Unsafe-data scope | “315 human-translated unsafe prompts in each of the 10 languages.” | [A.2 Prompt sets; PDF p. 8](https://aclanthology.org/2026.mrl-1.19.pdf#page=8) |
| Missing causal control | “We ran the control direction for the geometry” | [6 Ethics and limitations: The decisive control we did not run; PDF p. 6](https://aclanthology.org/2026.mrl-1.19.pdf#page=6) |

**Effect on candidate gap - reviewer interpretation.** Establishes cross-lingual refusal-mechanism analysis while leaving behavioral causal controls incomplete.

## E05: Pag-refuse: Safety Alignment Transfers Unevenly to Tagalog and Taglish

Paper ID: [2026.mrl-1.41](https://aclanthology.org/2026.mrl-1.41/).

**Problem and method.** The authors investigate whether refusal behavior learned predominantly through English safety training transfers to Tagalog and natural Taglish, and whether ordinary code-switching increases or reduces harmful compliance relative to monolingual Tagalog. They also examine variation across model families, sizes, and harm domains. The authors construct parallel English–Tagalog–Taglish prompt families from StrongREJECT. Kimi K3 drafts translations, and the two native-Tagalog-speaking authors audit and revise every translation. Responses receive mutually exclusive jailbreak, not-jailbreak, or irrelevant labels from two independent LLM judges, with author adjudication of disagreements. Materially useful harmful content counts as a jailbreak even when accompanied by warnings.

**Data and experiment.** The dataset contains all 313 StrongREJECT requests in three language conditions, totaling 939 prompts and 27,042 observed model responses. Six harm domains are represented: illegal goods and services, hate and harassment, violence, disinformation, non-violent crimes, and sexual content. Taglish translations preserve Tagalog grammar while borrowing English vocabulary. English originals serve as paired baselines for Tagalog and Taglish across 29 models from Anthropic, DeepSeek, Google, Meta, Mistral, OpenAI, xAI, Z.ai, and Qwen. Comparisons include multiple sizes within Qwen3, Llama 3.1, Gemma 3, and Ministral 3. Models are accessed through OpenRouter using a common message schema; greedy decoding and seed 42 are requested where supported, with endpoint-specific exceptions and minimum reasoning effort where necessary.

**Author-stated limitation reviewed.** limitation: Model size is not isolated experimentally; parameter count is confounded with training and alignment differences between variants, so size-related patterns are descriptive.; pdf_page: 3

| Evidence topic | Exact short passage | Location |
|---|---|---|
| Native translation review | “The authors, who are native Tagalog speakers, then audited and revised” | [3.1 Prompt set and translation; PDF p. 2](https://aclanthology.org/2026.mrl-1.41.pdf#page=2) |
| Register coverage limitation | “Our translations cover one Tagalog variety and one Taglish register.” | [Limitations; PDF p. 5](https://aclanthology.org/2026.mrl-1.41.pdf#page=5) |

**Effect on candidate gap - reviewer interpretation.** Provides native-reviewed matched Tagalog/Taglish refusal evaluation and bounds claims about mixed-language novelty.

## Gap consequence

Singapore-focused toxicity, multilingual guardrails, over-refusal benchmarks, native-reviewed harmful-prompt sets and refusal mechanisms already exist. The candidate gap is a bounded matched evaluation of harmful and benign near-boundary scenario families in selected Singapore settings, with translation/register disagreement separated from unsafe compliance and false refusal.

This comparison set is deliberately challenging rather than exhaustive. A wider search remains required before a definitive novelty claim.
