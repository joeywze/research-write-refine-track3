#function: feedback and revision prompts

FEEDBACK_PROMPT = """
You are a critical academic writing reviewer.

Review the research paper below for clarity, specificity,
argument quality, and readability.

Identify concrete issues such as:
1. Repetitive sentence structures or phrases.
2. Generic claims that lack a clear explanation.
3. Weak logical connections between sentences or sections.
4. Vague descriptions of the research contribution.
5. Unnecessarily complex or monotonous sentence structures.
6. Overconfident claims that exceed the available evidence.
7. Missing limitations or uncertainty where scientifically relevant.

Important constraints:
- Do not assume that formal academic language is AI-generated.
- Do not recommend changing text merely to fool AI detectors.
- Do not invent weaknesses, citations, data, or scientific claims.
- Distinguish stylistic problems from scientific problems.
- Give specific examples from the draft.
- Prioritize the five most important improvements.
- Explain why each change would improve the writing.

Return feedback using this structure:

OVERALL ASSESSMENT:
...

PRIORITY 1:
Problem:
Evidence from draft:
Recommended change:

PRIORITY 2:
Problem:
Evidence from draft:
Recommended change:

Continue up to PRIORITY 5.

PRESERVATION REQUIREMENTS:
List any scientific claims, numbers, citations, or technical details
that must remain unchanged.

PAPER:
{paper}
"""


REWRITE_PROMPT = """
You are revising an academic research paper based on reviewer feedback.

CURRENT DRAFT:
{paper}

REVIEWER FEEDBACK:
{feedback}

Revise the draft according to the feedback.

Requirements:
1. Preserve the original research question and intended contribution.
2. Preserve factual claims, numerical results, and citation details.
3. Do not fabricate experiments, results, references, or evidence.
4. Do not turn hypothetical results into completed experiments.
5. Retain appropriate technical terminology.
6. Improve clarity, argumentation, specificity, and sentence variety
   where the feedback justifies doing so.
7. Preserve relevant limitations and uncertainty.
8. Do not make changes solely to evade AI-detection systems.
9. Keep all existing paper sections and their headings.
10. Return the complete revised paper, not a summary of changes.

If feedback suggests a change that would require new evidence,
do not invent that evidence. Retain the limitation or flag it
for human review.

Return only the revised paper.
"""