# Half 2 change report

3 of 3 selected paragraphs revised; 0 kept as written. Mean detector score on selected paragraphs: 85.0 -> 53.2.

| Paragraph | Score | Outcome | Attempts | Last verdict |
|---|---|---|---|---|
| P035 | 92 -> 56 | revised | 3 | rejected by detector: score 58 is not below the best safe version (56) |
| P037 | 87 -> 70 | revised | 3 | rejected by detector: score 70 is not below the best safe version (70) |
| P002 | 75 -> 34 | revised | 1 | passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check) |

## P035 (experiments)

Why selected: detector score 92; stock phrases, hedge density, lists of three.
- Attempt 1: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check); still scores 72 (target 35), trying to lower it further
- Attempt 2: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check); still scores 56 (target 35), trying to lower it further
- Attempt 3: rejected by detector: score 58 is not below the best safe version (56)

**Before:** Exploratory 95% bootstrap intervals will resample whole underlying items, retaining their translations, answer variants and repeated calls together. With a small sample, intervals may be wide or degenerate; such outcomes and undefined statistics will be reported rather than replaced by favorable summaries. A non-significant contrast will not establish cross-language equivalence.

**After:** Exploratory 95% bootstrap intervals will resample whole underlying items so that each item’s translations stay with its answer variants and repeated calls. With a small sample, intervals can be wide or degenerate. Those outcomes, and undefined statistics, will be reported instead of replaced by favorable summaries. A non-significant contrast will not establish cross-language equivalence.

## P037 (experiments)

Why selected: detector score 87; hedge density, lists of three, sentence lengths are too uniform.
- Attempt 1: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check); still scores 70 (target 35), trying to lower it further
- Attempt 2: rejected by meaning check: Semantic check failed: ValueError: checked_claim_ids: duplicate entries
- Attempt 3: rejected by detector: score 70 is not below the best safe version (70)

**Before:** The design is limited to one selected language pair, one primary judge, a small sample and constructed short-answer errors. It cannot establish broad multilingual fairness, deployment safety or performance across model families. Minimal errors may be too easy or unrepresentative of naturally generated answers, creating ceiling effects that this pilot would need to identify.

**After:** The design is limited to one selected language pair, one primary judge, a small sample, and constructed short-answer errors. It cannot establish broad multilingual fairness, deployment safety, or performance across model families. That is a pilot limitation. Minimal errors may be too easy or unrepresentative of naturally generated answers, which would create ceiling effects that this pilot would need to identify.

## P002 (introduction)

Why selected: detector score 75; stock phrases, lists of three, sentence lengths are too uniform.
- Attempt 1: passed all checks (fluency guard, preservation rules, no new facts, evidence check, meaning check)

**Before:** When a language model is used to evaluate answers, the evaluator itself becomes an object of assessment. Multilingual studies already examine this problem: Fu and Liu evaluate judgments on parallel language versions, while Chung and Freienthal investigate cross-language stability in controlled customer-support dialogues. Their work provides direct precedents for studying language-dependent evaluation, rather than a basis for claiming that multilingual judging has been overlooked.

**After:** When a language model is used to evaluate answers, the evaluator itself becomes an object of assessment. Multilingual studies already examine this problem. Fu and Liu evaluate judgments on parallel language versions, and Chung and Freienthal investigate cross-language stability in controlled customer-support dialogues. Their work gives direct precedents for studying language-dependent evaluation; it does not support a claim that multilingual judging has been overlooked.
