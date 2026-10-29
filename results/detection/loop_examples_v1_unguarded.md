# Before / after examples (detector-guided)

## GPT-1290-introduction-1 (GPT pilot)

**Before - score 95**

Our results indicate that fLSA learns tags that preserve more of the structure needed to recover the original documents than the considered existing tagging approaches. Furthermore, when used to organize sampling, the learned tags broaden generation in semantically meaningful directions and more frequently lead to correct solutions than direct sampling or hierarchical sampling with the alternative tag representations. These findings suggest that foundation models can be used not only as generators, but also as tools for inducing reusable semantic abstractions from document collections.

**Naive prompt after 4 rounds - score 96**

Our results show that fLSA learns tags that preserve more of the structure needed to recover the original documents than the existing tagging approaches we considered. When used to organize sampling, these tags guide generation along semantically meaningful directions and produce correct solutions more often than direct sampling or hierarchical sampling with the alternative tag representations. Together, these findings suggest that foundation models can function not only as generators but also as tools for inducing reusable semantic abstractions from document collections.

**Detector-guided after 4 rounds - score 16**

Our results indicate that fLSA learns tags that preserve more of the structure needed to recover the original documents than the considered existing tagging approaches. Sampling changes. When learned tags organize sampling, they broaden generation along directions that reflect semantic structure and more frequently lead to correct solutions than direct sampling or hierarchical sampling with the alternative tag representations. Foundation models can serve both as generators and as tools for inducing reusable semantic abstractions from document collections.

## V0-P037 (our draft V0)

**Before - score 87**

The design is limited to one selected language pair, one primary judge, a small sample and constructed short-answer errors. It cannot establish broad multilingual fairness, deployment safety or performance across model families. Minimal errors may be too easy or unrepresentative of naturally generated answers, creating ceiling effects that this pilot would need to identify.

**Naive prompt after 4 rounds - score 84**

The design is limited to one selected language pair, one primary judge, a small sample, and constructed short-answer errors, so it cannot establish broad multilingual fairness, deployment safety, or performance across model families. The minimal errors may also be too easy or unlike naturally generated answers, creating ceiling effects that this pilot would need to detect.

**Detector-guided after 4 rounds - score 14**

The design is limited to one selected language pair and one primary judge. It uses a small sample and constructed short-answer errors. The scope is narrow. It cannot establish broad multilingual fairness or deployment safety. Nor can it establish performance across model families. It is uncertain whether minimal errors are too easy or unrepresentative of naturally generated answers; if so, they would create ceiling effects that this pilot would need to identify.

## GPT-.415-related_work-2 (GPT pilot)

**Before - score 96**

Sociolinguistic research has long shown that dialects are evaluated not only as linguistic varieties but also as signals of social identity, regional belonging, and group membership. Although dialect use is often associated with solidarity and authenticity within local communities, speakers may also be judged through stereotypes concerning intelligence, competence, education, trustworthiness, or social status. These evaluations can vary according to the listener, the social context, and the perceived prestige of the dialect. Standard-language varieties are frequently treated as more appropriate in institutional and formal settings, while regional varieties may be framed as informal, less prestigious, or less suitable for professional communication. Work on German language attitudes similarly documents the coexistence of regional pride and negative judgments toward speakers of particular dialects. This literature motivates examining dialect bias as a multidimensional phenomenon rather than assuming that all regional varieties receive the same social evaluation.

**Naive prompt after 4 rounds - score 98**

Sociolinguistic research has long shown that dialects are judged not only as linguistic varieties but also as markers of social identity, regional belonging, and group membership. In local communities, dialect use is often linked to solidarity and authenticity, but speakers may also encounter stereotypes concerning their intelligence, competence, education, trustworthiness, or social status. These judgments depend on the listener, the social context, and the perceived prestige of the dialect. Standard-language varieties are generally viewed as more appropriate in institutional and formal settings, while regional varieties may be considered informal, less prestigious, or less suitable for professional communication. Research on German language attitudes similarly indicates that regional pride can coexist with negative judgments of speakers of particular dialects. This body of work therefore supports treating dialect bias as a multidimensional phenomenon rather than assuming that all regional varieties receive the same social evaluation.

**Detector-guided after 4 rounds - score 29**

Sociolinguistic research has long shown that dialects are evaluated as linguistic varieties and signal social identity. Dialects can indicate regional belonging and group membership. Dialect use often conveys solidarity and authenticity within local communities. Yet stereotypes about intelligence can shape how speakers are judged. Competence is judged similarly. Education influences these judgments. Trustworthiness does too. Social status also matters. The listener and social context partly determine these effects. The dialect’s perceived prestige matters. Standard-language varieties are frequently treated as more appropriate in institutional and formal settings, whereas regional varieties are often framed as informal or less prestigious and viewed as less suitable for professional communication. Work on German language attitudes similarly documents both regional pride and negative judgments toward speakers of particular dialects. This literature motivates examining dialect bias as a multidimensional phenomenon. Regional varieties do not all receive the same social evaluation.
