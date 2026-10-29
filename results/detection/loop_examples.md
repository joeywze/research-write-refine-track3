# Before / after examples (detector-guided)

## GPT-1290-introduction-1 (GPT pilot)

**Before - score 95**

Our results indicate that fLSA learns tags that preserve more of the structure needed to recover the original documents than the considered existing tagging approaches. Furthermore, when used to organize sampling, the learned tags broaden generation in semantically meaningful directions and more frequently lead to correct solutions than direct sampling or hierarchical sampling with the alternative tag representations. These findings suggest that foundation models can be used not only as generators, but also as tools for inducing reusable semantic abstractions from document collections.

**Naive prompt after 4 rounds - score 96**

Our results show that fLSA learns tags that preserve more of the structure required to recover the original documents than the existing tagging approaches we considered. When used to organize sampling, these tags steer generation in semantically meaningful directions and produce correct solutions more often than direct sampling or hierarchical sampling with the alternative tag representations. Together, these findings suggest that foundation models can function not only as generators but also as tools for inducing reusable semantic abstractions from document collections.

**Detector-guided after 4 rounds - score 29**

Our results show that fLSA learns tags that preserve more of the structure needed to recover the original documents than the existing tagging approaches considered here. For sampling, the learned tags broaden generation along directions tied to semantic structure and more frequently lead to correct solutions than direct sampling or hierarchical sampling with the alternative tag representations. Foundation models function as both generators and tools for inducing reusable semantic abstractions from document collections.

## V0-P037 (our draft V0)

**Before - score 87**

The design is limited to one selected language pair, one primary judge, a small sample and constructed short-answer errors. It cannot establish broad multilingual fairness, deployment safety or performance across model families. Minimal errors may be too easy or unrepresentative of naturally generated answers, creating ceiling effects that this pilot would need to identify.

**Naive prompt after 4 rounds - score 88**

This design is limited to one selected language pair, one primary judge, a small sample, and constructed short-answer errors. As a result, it cannot establish broad multilingual fairness, deployment safety, or performance across model families. Minimal errors may also be too easy or unrepresentative of naturally generated answers, creating ceiling effects that this pilot would need to identify.

**Detector-guided after 4 rounds - score 30**

The design covers only one selected language pair and uses one primary judge. It also relies on a small sample and constructed short-answer errors. It cannot establish broad multilingual fairness, deployment safety, or performance across model families. The unresolved question is whether minimal errors are too easy or unrepresentative of naturally generated answers; either condition would create ceiling effects that this pilot would need to identify.

## GPT-1371-related_work-0 (GPT pilot)

**Before - score 96**

Studies of knowledge conflicts have examined how language models respond when prompts contain information that differs from their stored knowledge. These investigations suggest that models may follow contextual information even when it is misleading, while in other cases they may disregard valid evidence because of strong parametric priors. The outcome can depend on factors such as the position, salience, phrasing, and apparent credibility of the context. Such findings motivate methods that explicitly model the reliability of retrieved information rather than treating all context tokens as equally trustworthy.

**Naive prompt after 4 rounds - score 98**

Studies of knowledge conflicts investigate how language models respond when prompts include information that differs from what they have stored. Research shows that models may follow misleading contextual information, yet they may also ignore valid evidence when it conflicts with strong parametric priors. Outcomes can depend on the context’s position, salience, phrasing, and perceived credibility. These findings motivate methods that explicitly model the reliability of retrieved information rather than treating all context tokens as equally trustworthy.

**Detector-guided after 4 rounds - score 43**

Studies of knowledge conflicts have examined how language models respond when prompts contain information that differs from their stored knowledge. These investigations suggest that models sometimes follow misleading contextual information, but they can also disregard valid evidence when strong parametric priors favor another answer. The outcome can depend on where the context appears and how it is phrased; its salience and apparent credibility also matter. Context is not uniformly trustworthy. Methods should model the reliability of retrieved information and assign different levels of trust to context tokens.
