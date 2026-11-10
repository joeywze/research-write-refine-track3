# Half 2 change report

3 of 4 selected paragraphs revised; 1 kept as written. Mean detector score on selected paragraphs: 52.9 -> 37.0.

| Paragraph | Score | Outcome | Attempts | Last verdict |
|---|---|---|---|---|
| P014 | 65 -> 37 | revised | 3 | rejected by detector: score 37 is not below the best safe version (37) |
| P001 | 61 -> 35 | revised | 1 | passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check) |
| P026 | 43 -> 43 | kept original | 3 | rejected by fluency guard: too many very short sentences |
| P027 | 42 -> 33 | revised | 3 | passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check) |

## P014 (methodology)

Why selected: detector score 65; stock phrases, share of very long sentences, lists of three.
- Attempt 1: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check); still scores 37 (target 35), trying to lower it further
- Attempt 2: rejected by detector: score 37 is not below the best safe version (37)
- Attempt 3: rejected by detector: score 37 is not below the best safe version (37)

**Before:** The planned pilot contains 20 underlying passage–question items. Each item will have a correct answer and a minimally altered incorrect answer in both languages, yielding 80 response texts before exclusions. Incorrect variants will change a substantive entity, quantity or relation while keeping the answer form as similar as practical. Human review will verify that a variant is actually incorrect rather than an alternative valid expression.

**After:** The planned pilot contains 20 underlying passage–question items. Each item will have a correct answer and a minimally altered incorrect answer in both languages, yielding 80 response texts before exclusions. Incorrect variants will change a substantive entity, quantity, or relation while keeping the answer form as similar as practical. Human review will verify that a variant is genuinely incorrect, not an alternative valid expression.

## P001 (abstract)

Why selected: detector score 61; share of very long sentences, stock phrases, sentence lengths are too uniform.
- Attempt 1: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check)

**Before:** Agreement with human judgments, consistency across languages and stability across repeated calls describe different aspects of an automated evaluator. A judge may produce stable decisions that are nevertheless incorrect, or agree with humans in one language but not on a meaning-matched version in another. We propose a controlled bilingual study that measures these properties separately in context-grounded short question answering. A feasibility pilot will contain 20 passage–question items, each with a correct and a deliberately incorrect answer in English and one additional language. Two fluent raters will independently assess each response before adjudication. One fixed language-model judge will evaluate the responses under English instructions, with an additional target-language instruction condition and three calls per condition. The analysis will separate human-reference agreement, cross-language decision changes, repeated-call stability and non-decisions. The proposed contribution is a human-validated replication-and-extension protocol for a bounded QA setting, rather than a claim to introduce multilingual judging. The study is designed to distinguish incorrect judgments from unstable judgments and data-construction problems; no direction of effect is assumed.

**After:** Agreement with human judgments is one issue. Consistency across languages is another, and stability across repeated calls is a third. These aspects of an automated evaluator can come apart: a judge may produce stable decisions that are nevertheless incorrect, or agree with humans in one language but not on a meaning-matched version in another. We propose a controlled bilingual study that measures these properties separately in context-grounded short question answering. A feasibility pilot will contain 20 passage–question items, each with a correct and a deliberately incorrect answer in English and one additional language. Two fluent raters will independently assess each response before adjudication. One fixed language-model judge will evaluate the responses under English instructions, with an additional target-language instruction condition and three calls per condition. The analysis will separate human-reference agreement, cross-language decision changes, repeated-call stability, and non-decisions. The proposed contribution is a human-validated replication-and-extension protocol for a bounded QA setting, not a claim to introduce multilingual judging. The study is designed to distinguish incorrect judgments from unstable judgments and data-construction problems; no direction of effect is assumed.

## P026 (methodology)

Why selected: detector score 43; sentence lengths are too uniform, share of very long sentences, lists of three.
- Attempt 1: rejected by detector: score 43 is not at least 5 points below 43
- Attempt 2: rejected by detector: score 56 is not at least 5 points below 43
- Attempt 3: rejected by fluency guard: too many very short sentences

**Before:** Each response/condition will receive three calls in separate contexts without previous verdicts. The model configuration and prompt template will be fixed within a condition. Full prompts, raw outputs, versions, dates, supported sampling controls, token limits, parsing decisions and technical failures will be recorded. Fixing settings defines the repeatability test; it does not guarantee deterministic outputs.

**After:** Each response/condition will receive three calls in separate contexts without previous verdicts. The model configuration and prompt template will be fixed within a condition. Full prompts, raw outputs, versions, dates, supported sampling controls, token limits, parsing decisions and technical failures will be recorded. Fixing settings defines the repeatability test; it does not guarantee deterministic outputs.

## P027 (experiments)

Why selected: detector score 42; sentence lengths are too uniform, share of very long sentences, lists of three.
- Attempt 1: rejected by meaning check: Semantic check failed: ValueError: checked_claim_ids: duplicate entries
- Attempt 2: rejected by detector: score 42 is not at least 5 points below 42
- Attempt 3: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check)

**Before:** With 20 qualifying items, there will be 40 candidate responses per content language. Each of the three conditions requires 40 responses × 3 calls, giving 360 scheduled J1 calls. Initial human annotation requires 80 response texts × 2 ratings, or 160 ratings. Translation review, practice, adjudication and any technical retries add workload. An optional J2 would require another 360 calls.

**After:** With 20 qualifying items, there will be 40 candidate responses per content language. Each of the three conditions requires 40 responses × 3 calls, giving 360 scheduled J1 calls. Initial human annotation requires 80 response texts × 2 ratings, or 160 ratings. Translation review, practice, adjudication, plus any technical retries, add workload. An optional J2 would require another 360 calls.
