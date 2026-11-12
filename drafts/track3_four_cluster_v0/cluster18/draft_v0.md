# Safe and Useful Across Singapore Language Settings: A Matched Evaluation of Unsafe Compliance and False Refusal

Draft V0 — revised 5 November 2026 after full-text review of all 16 Cluster 18 papers and 5 close 2026 papers. Proposed study; no experimental results are reported. Harmful prompt content is not reproduced in this draft.

## Abstract

Multilingual safety evaluation must distinguish two opposing failures: complying with harmful requests and refusing benign requests that resemble them. Existing research already provides Singapore-focused toxicity data, multilingual guardrails, over-refusal benchmarks, native-reviewed harmful-prompt sets and mechanistic analyses of refusal. The defensible gap is therefore a bounded replication-and-extension: matched harmful and benign near-boundary scenarios evaluated in selected Singapore language settings, with translation and register quality adjudicated independently of model safety. We propose English plus two settings chosen only after recruiting fluent reviewers. Sixty scenario families will be translated, naturally rewritten and reviewed for intent, harm status and equivalence. Two language models and one external guardrail will be tested over repeated calls. Response labels will separate unsafe compliance, safe assistance, appropriate refusal, false refusal, redirection and technical failure. The scenario—not the individual prompt variant—will be the comparison unit. The contribution is a transparent paired protocol that keeps safety, usefulness and language-equivalence errors separate; it is not the first multilingual safety benchmark and does not generalize to entire language communities.

## 1. Introduction

A model can appear safe by refusing nearly everything. It can appear helpful by answering requests that should have been refused. A valid safety evaluation must therefore measure unsafe compliance on harmful inputs and false refusal on benign inputs. In multilingual settings, a third problem intervenes: a translated or code-switched prompt may alter intent, severity, politeness or local meaning. Without independent equivalence review, a changed model outcome can be misattributed to language.

The Cluster 18 papers establish that this broad space is already active. RASS evaluates both over- and under-refusal, while SGToxicGuard provides a Singapore-focused toxicity dataset spanning Singlish, Chinese, Malay and Tamil. MrGuard and OMNIGUARD evaluate multilingual guardrails. The reviewed work also warns that model-based safety judges are fallible and that some evaluations contain limited human review. [RASS, 2025, over-/under-refusal design, p. 4](https://aclanthology.org/2025.emnlp-main.49.pdf#page=4); [RASS, evaluator limitation, p. 9](https://aclanthology.org/2025.emnlp-main.49.pdf#page=9); [SGToxicGuard, task construction, p. 4](https://aclanthology.org/2025.emnlp-main.612.pdf#page=4); [SGToxicGuard, judge limitation, p. 9](https://aclanthology.org/2025.emnlp-main.612.pdf#page=9).

The close 2026 literature narrows the gap again. Pag-refuse uses native-reviewed Tagalog and Taglish prompts; BanglaSafe uses native and expert review for culturally grounded harmful requests; cross-lingual refusal work studies shared refusal mechanisms. These papers block claims that native review, mixed-language safety or lower-resource settings have been ignored. [Pag-refuse, 2026, native review, p. 2](https://aclanthology.org/2026.mrl-1.41.pdf#page=2); [BanglaSafe, 2026, review process, p. 5](https://aclanthology.org/2026.findings-emnlp.1403.pdf#page=5).

The proposed study asks a smaller question: under matched harmful/benign scenario pairs, do selected systems preserve the safety–usefulness boundary across English and two Singapore language settings after ambiguous or non-equivalent items are separated?

1. **RQ1—Safety:** How does unsafe-compliance rate on harmful scenarios differ across settings?
2. **RQ2—Usefulness:** How does false-refusal rate on benign near-boundary scenarios differ across settings?
3. **RQ3—Equivalence:** How much apparent cross-language change is concentrated in items with reviewer disagreement about meaning, intent or register?
4. **RQ4—Guardrail interaction:** Where do an external prompt guardrail and the final model response fail independently or together?

No direction of effect is assumed. The study is an audit, not a mitigation method.

## 2. Related Work and Gap Establishment

### 2.1 Singapore and multilingual safety are not missing

SGToxicGuard directly establishes Singapore relevance by evaluating multilingual and local-language toxicity across conversation, question answering and content composition. MrGuard evaluates multilingual harmful-input detection and reports a seven-language setting, although its white-box dependence limits some deployment comparisons. OMNIGUARD/MULTIGUARD covers multilingual and perturbed inputs. [MrGuard, 2025, language coverage, p. 3](https://aclanthology.org/2025.emnlp-main.1065.pdf#page=3); [MrGuard, white-box limitation, p. 9](https://aclanthology.org/2025.emnlp-main.1065.pdf#page=9).

The proposal therefore does not claim a new language list or a first local benchmark. It selects a small set of settings to make human review feasible and to test a specific matched design.

### 2.2 Harmful-only evaluation is insufficient

Some benchmarks emphasize unsafe prompts without a matched benign control. MrGuard's evaluation assumes harmful inputs for parts of its analysis and reports limited human review. BanglaSafe's native-reviewed benchmark is valuable but does not supply the benign near-boundary control needed to estimate false refusal in the same design. [MrGuard, unsafe-only assumption, p. 13](https://aclanthology.org/2025.emnlp-main.1392.pdf#page=13); [MrGuard, human-review limitation, p. 9](https://aclanthology.org/2025.emnlp-main.1392.pdf#page=9); [BanglaSafe, absence of benign control noted in limitations, p. 9](https://aclanthology.org/2026.findings-emnlp.1403.pdf#page=9).

Pag-refuse provides an especially close precedent for matched refusal evaluation in one language and a mixed-language variety. Its authors appropriately limit inference to a particular variety/register. Our study extends the control principle to selected Singapore settings rather than claiming broad cross-lingual coverage. [Pag-refuse, limitation, p. 5](https://aclanthology.org/2026.mrl-1.41.pdf#page=5).

### 2.3 Mechanistic findings do not replace outcome controls

Cross-lingual refusal-direction research studies internal representations using unsafe data. The authors note that causal controls remain incomplete, so mechanistic similarity should not be substituted for a behavioral safety–usefulness audit. [Cross-Lingual Refusal Direction, 2026, unsafe-data design, p. 8](https://aclanthology.org/2026.mrl-1.19.pdf#page=8); [causal-control limitation, p. 6](https://aclanthology.org/2026.mrl-1.19.pdf#page=6).

The gap supported by these papers is thus a combination of matched harmful/benign boundaries, independent equivalence review and joint guardrail–response analysis in selected Singapore settings.

## 3. Methodology

### 3.1 Language-setting selection

English and two additional settings will be selected only after confirming two fluent reviewers and one adjudicator for each. Candidate settings may include a standardized language, a Singapore variety or a code-switched register, but the final choice will be based on reviewer competence and feasible ethical oversight—not a hierarchy of “resource level.”

The unit of inference will be the selected setting and prompt set. Results will not be generalized to all speakers, dialects or countries associated with a language.

### 3.2 Scenario families and paired boundary construction

We plan 60 underlying scenario families across a small number of safety categories. Each family will contain:

- a harmful request whose requested action violates the frozen policy;
- a benign near-boundary request sharing topic or vocabulary but changing intent, target or requested action;
- where feasible, a clearly benign anchor to distinguish boundary difficulty from global refusal.

Existing licensed benchmark items will be adapted where their terms permit; new items require safety review. Prompts will omit unnecessary operational details. The harmful and benign forms will be similar enough to test discrimination without being simple word substitutions that create unnatural text.

The following is a structural illustration only, not an evaluation item:

| Variant | Intended status | Difference |
|---|---|---|
| Harmful | Refuse or safely redirect | Requests actionable harm |
| Near-boundary benign | Assist safely | Requests prevention, recognition or recovery information |
| Benign anchor | Assist | Clearly ordinary informational request |

### 3.3 Translation, naturalization and equivalence review

English scenarios will be translated and then naturally rewritten for the target setting. Two fluent reviewers will independently label:

1. harm status under the shared policy;
2. requested intent and target;
3. severity/category;
4. naturalness and register;
5. semantic equivalence to the English scenario;
6. ambiguity.

Reviewers will provide reasons for disagreement. An adjudicator will resolve cases where possible before model testing. If one member of a scenario family remains non-equivalent or ambiguous, the complete family is excluded from the primary paired analysis and retained in an equivalence-sensitivity appendix. Exclusion rules will be frozen before model outcomes are seen.

### 3.4 Models, guardrail and repeated calls

Two instruction-tuned model families and one external input guardrail will be selected based on reproducible access and multilingual support. Model and guardrail versions, dates, system policies, prompts, sampling controls and token limits will be recorded. Each model–prompt condition will receive three independent calls.

The guardrail first classifies the input. The model response is still collected where ethically and technically permitted under a controlled protocol, enabling a two-stage error analysis. No system will be prompted to provide more harmful detail merely to overcome a refusal.

### 3.5 Response annotation

Two fluent raters, blinded to system identity where feasible, will independently assign:

| Label | Decision rule |
|---|---|
| Appropriate refusal | Declines harmful assistance without supplying actionable content |
| Safe redirection | Declines the harmful action and offers relevant prevention/recovery help |
| Unsafe compliance | Supplies materially actionable harmful assistance |
| Safe assistance | Answers a benign request without unnecessary restriction |
| False refusal | Refuses or withholds useful help on a benign request |
| Partial/ambiguous | Mixed response that does not meet a primary rule |
| Invalid/technical failure | No usable response |

Model-based judges may support triage but will not replace human outcome labels, because the reviewed literature documents evaluator fallibility. Disagreements will be adjudicated and raw agreement reported.

## 4. Experiments and Evaluation Plan

### 4.1 Primary outcomes

The two primary rates are:

- **unsafe-compliance rate:** harmful calls labeled unsafe compliance;
- **false-refusal rate:** benign calls labeled false refusal.

Safe redirection, appropriate refusal, safe assistance, partial responses and failures remain separate. Reporting only “refusal rate” would collapse desirable and undesirable behavior.

The underlying scenario family is the resampling unit. Prompt variants, languages and repeat calls derived from it remain linked. Paired cross-setting differences and scenario-cluster bootstrap intervals will be reported separately by model before any pooled result.

### 4.2 Repeated-call stability

For each prompt–model cell, we will report whether all three outcomes agree and whether any unsafe compliance occurred. Three calls offer only a coarse instability check; they do not estimate a production probability precisely. Technical failures count in operational coverage and are not silently retried beyond the frozen rule.

### 4.3 Guardrail–response error table

Guardrail classification and model response will be crossed:

| Guardrail | Final response | Interpretation |
|---|---|---|
| Allows harmful input | Unsafe compliance | Shared safety failure |
| Allows harmful input | Appropriate refusal/redirection | Model catches what guardrail misses |
| Blocks benign input | No useful answer | Guardrail-driven false refusal |
| Allows benign input | False refusal | Model-driven over-refusal |

This table separates input filtering from response behavior. It does not imply that bypassing a provider guardrail is acceptable.

### 4.4 Equivalence sensitivity and interpretation

Primary results use only fully adjudicated matched families. A sensitivity analysis will include disputed-but-usable items with an equivalence indicator. If outcome changes are concentrated among disputed translations, we will describe a data-quality interaction rather than a language-safety deficit.

Prospective interpretations include:

| Pattern | Interpretation |
|---|---|
| Unsafe compliance rises; equivalence is strong | Model safety difference in the tested setting |
| False refusal rises while unsafe compliance falls | Safety–usefulness trade-off |
| Both rates rise | Poorer boundary discrimination |
| Differences concentrate in disputed items | Translation/register quality is a plausible driver |
| Guardrail and model fail on different items | Potential complementarity, requiring further testing |

### 4.5 Ethics, feasibility and limitations

Reviewers may encounter distressing material. The protocol requires informed consent, category-level warnings, the ability to skip items, limited exposure, secure storage and a named escalation route. No personally identifying or targeted harmful content will be collected.

A six-family pilot will test translation, naturalization, agreement and annotation burden. Pilot prompts will be excluded if instructions change. The final study remains small and bounded. It cannot estimate safety for an entire language community; provider policies differ; human labels are fallible; model and guardrail versions can drift; repeated calls are few; and matched prompts may be less natural than organically occurring misuse. The study measures observed behavior under specified conditions, not inherent safety of a language.

## 5. Conclusion

Singapore-focused toxicity, multilingual guardrails and native-reviewed refusal benchmarks already exist. The credible contribution is a narrower matched audit that evaluates unsafe compliance and false refusal together while separating language-equivalence problems from model outcomes. The design makes it possible for the proposed claim to fail and avoids treating blanket refusal as safety. Experimental results remain to be collected.

## References

- 2025. [RASS: A Multilingual Benchmark for Refusal and Over-Refusal](https://aclanthology.org/2025.emnlp-main.49/).
- Hu et al. 2025. [SGToxicGuard](https://aclanthology.org/2025.emnlp-main.612/).
- Verma et al. 2025. [MULTIGUARD/OMNIGUARD](https://aclanthology.org/2025.emnlp-main.819/).
- Pan et al. 2025. [Understanding and Mitigating Overrefusal](https://aclanthology.org/2025.emnlp-main.1065/).
- Yang et al. 2025. [MrGuard](https://aclanthology.org/2025.emnlp-main.1392/).
- Albayda and Naguio. 2026. [Pag-refuse](https://aclanthology.org/2026.mrl-1.41/).
- Qi et al. 2026. [Adaptive Contrastive Decoding](https://aclanthology.org/2026.acl-long.1823/).
- Zhang. 2026. [Cross-Lingual Refusal Direction](https://aclanthology.org/2026.mrl-1.19/).
- 2026. [BanglaSafe](https://aclanthology.org/2026.findings-emnlp.1403/).
- 2026. [Multilingual Safety Evaluation](https://aclanthology.org/2026.findings-acl.1537/).
