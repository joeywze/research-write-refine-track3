"""Seeded-fault test: ground truth for the Half 2 checks.

We take real V0 paragraphs and plant one known error in each (a changed number,
a dropped citation, a made-up result, a misstated source...). Because we planted
the error, the correct verdict (REJECT) is known before any check runs. Clean
rewrites that keep the meaning should be ACCEPTED. Running every case through
the checks gives a catch rate per fault type and a false-alarm rate.

Every case is spelled out below as "find this text, replace it with that", so a
teammate can read and verify each label. The `verified` column starts as "no":
set it to "yes" after checking a case by hand.

Usage (from sprint2_demo/):
  python seeded_faults.py build                    # writes evaluation/seeded_faults.csv
  python seeded_faults.py run                      # rule-based checks only, no API key needed
  python seeded_faults.py run --llm --checker-model <model> [--labelled-only]   # adds evidence and meaning checks
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

import pandas as pd

from project_io import read_input
import half2_checks as checks

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs" / "converted"
EVAL = HERE / "evaluation"
CASES_FILE = EVAL / "seeded_faults.csv"
V3_FILE = HERE.parent / "results" / "detection" / "full_paper" / "paragraphs.csv"

# (case_id, paragraph, fault_type, find, replace, which check we expect to catch it)
FAULTS = [
    # Numbers changed: digits are caught by rules; numbers written as words need a model.
    ("N1", "P027", "number changed", "360 scheduled J1 calls", "300 scheduled J1 calls", "rules"),
    ("N2", "P001", "number changed", "20 passage–question items", "30 passage–question items", "rules"),
    ("N3", "P027", "number changed", "or 160 ratings", "or 120 ratings", "rules"),
    ("N4", "P001", "number changed", "three calls per condition", "five calls per condition", "model"),
    ("N5", "P007", "number changed", "across six target languages", "across eight target languages", "model"),
    # Citations dropped, swapped or misattributed.
    ("C1", "P002", "citation changed", "[[S01]]; [[S02]].", "[[S01]].", "rules"),
    ("C2", "P007", "citation changed", "[[S03]]; [[S04]].", "[[S05]]; [[S04]].", "rules"),
    ("C3", "P008", "citation changed", "[[S05]]; [[S06]].", "[[S05]]; [[S06]]; [[S01]].", "rules"),
    ("C4", "P007", "citation changed", "[[S03]]; [[S04]].", "[[S03]].", "rules"),
    ("C5", "P008", "citation changed", "Yu et al. compare", "Fu and Liu compare", "model"),
    # Claims made stronger or flipped.
    ("S1", "P001", "claim strengthened", "A judge may produce stable decisions", "A judge clearly produces stable decisions", "rules"),
    ("S2", "P012", "claim strengthened", "This restriction makes the object of evaluation explicit",
     "This restriction guarantees that the object of evaluation is explicit", "rules"),
    ("S3", "P013", "claim strengthened", "the study is not designed to estimate a general effect",
     "the study is designed to estimate a general effect", "model"),
    ("S4", "P039", "claim strengthened", "The evaluation plan does not presume a language disadvantage or an improvement",
     "The evaluation plan expects a language disadvantage rather than an improvement", "model"),
    ("S5", "P034", "claim strengthened", "it does not make the two calls shared random draws or independent item samples",
     "so the two calls can be treated as independent item samples", "model"),
    # Made-up results in a proposal (no experiment has been run).
    ("R1", "P001", "made-up result", "no direction of effect is assumed.",
     "no direction of effect is assumed. Pilot results show that agreement drops in the second language.", "rules"),
    ("R2", "P039", "made-up result", "Experimental performance remains to be measured.",
     "Experimental performance improved markedly over earlier judges.", "rules"),
    ("R3", "P030", "made-up result", "they are not all interpreted as factual reasoning errors.",
     "they are not all interpreted as factual reasoning errors. In our pilot, this measure revealed differences between conditions.", "rules"),
    ("R4", "P021", "made-up result", "Raw labels and reasons will be retained.",
     "Raw labels and reasons were retained, and the raters agreed on most items.", "model"),
    ("R5", "P027", "made-up result", "add workload.", "add workload, which the team completed within two weeks.", "model"),
    # Cited papers misstated: wording barely changes, so only the evidence check can see it.
    ("E1", "P002", "source misstated", "Fu and Liu evaluate judgments on parallel language versions",
     "Fu and Liu evaluate judgments only on English versions", "model"),
    ("E2", "P007", "source misstated",
     "Wang et al. explicitly limit their evaluation to English and identify multilingual judging as future work",
     "Wang et al. evaluate many languages and consider multilingual judging already solved", "model"),
    ("E3", "P008", "source misstated", "Chung and Freienthal include an Estonian instruction-language sensitivity check",
     "Chung and Freienthal find that Estonian instructions strongly change judge scores", "model"),
    ("E4", "P007", "source misstated", "Wu et al. examine translation evaluation across six target languages.",
     "Wu et al. examine translation evaluation across six target languages and report that judges prefer their own translations in every language.", "model"),
    ("E5", "P002", "source misstated", "cross-language stability in controlled customer-support dialogues",
     "cross-language stability in real customer-support dialogues collected from companies", "model"),
    # Protected technical terms changed.
    ("T1", "P031", "protected term changed", "Conditional Cohen's kappa", "Conditional agreement coefficient", "rules"),
    ("T2", "P030", "protected term changed", "**unconditional operational agreement**", "**overall agreement**", "rules"),
    ("T3", "P031", "protected term changed", "Conditional Cohen's kappa", "Conditional Cohen kappa", "rules"),

    # Fresh faults: written before testing and frozen. No rule was changed after running them.
    ("F1", "P028", "fresh fault", "not statistically derived requirements",
     "statistically derived to detect a language effect", "model"),
    ("F2", "P014", "fresh fault", "yielding 80 response texts", "yielding 160 response texts", "rules"),
    ("F3", "P023", "fresh fault", "the one-judge pilot will not support claims across judge families",
     "the pilot will support claims across judge families", "model"),
    ("F4", "P017", "fresh fault", "Bilingual review would check", "Machine translation would check", "model"),
    ("F5", "P008", "fresh fault", "Yu et al. compare an official English prompt with basic and instructional Chinese prompts",
     "Yu et al. compare English and Japanese prompts", "model"),
]

# Clean rewrites: same meaning, different wording. These should be ACCEPTED.
CLEAN = [
    ("K1", "P012", "This restriction makes the object of evaluation explicit and avoids",
     "Restricting the task in this way makes the object of evaluation explicit and avoids"),
    ("K2", "P013", "The language and item source have not yet been selected.",
     "Neither the language nor the item source has been selected yet."),
    ("K3", "P021", "Raw labels and reasons will be retained.", "We will keep the raw labels and their reasons."),
    ("K4", "P022", "Counts and reasons will be reported.", "We will report the counts and the reasons."),
    ("K5", "P030", "Agreement indicators will first be averaged across calls for each response and then across responses within a condition.",
     "Agreement indicators will be averaged across calls for each response first, then across responses within a condition."),
    ("K6", "P034", "For RQ3, the same agreement and stability measures will compare C with B.",
     "For RQ3, we will compare C with B using the same agreement and stability measures."),
    ("K7", "P039", "The contribution is a bounded, auditable replication-and-extension design.",
     "What we contribute is a bounded, auditable replication-and-extension design."),
    ("K8", "P002", "the evaluator itself becomes an object of assessment", "the evaluator itself has to be assessed"),
    ("K9", "P007", "For example, Wang et al. explicitly limit", "Wang et al., for instance, explicitly limit"),
    ("K10", "P008", "Judging-instruction language also needs to be distinguished from the language of the evaluated content.",
     "The language of the judging instructions also needs to be kept apart from the language of the evaluated content."),
    ("K11", "P001", "The analysis will separate human-reference agreement, cross-language decision changes, repeated-call stability and non-decisions.",
     "In the analysis, human-reference agreement, cross-language decision changes, repeated-call stability and non-decisions will be kept separate."),
    ("K12", "P031", "The primary paired contrast is agreement", "The main paired contrast is agreement"),
    ("K13", "P013", "The study will compare English with a second language, denoted L.",
     "We will compare English with a second language, which we call L."),
    ("K14", "P027", "Translation review, practice, adjudication and any technical retries add workload.",
     "Translation review, practice, adjudication and any technical retries will add to this workload."),
]


def build():
    _, v0, _ = read_input(INPUTS)
    text_of = {p.paragraph_id: p.text for p in v0.paragraphs}
    rows = []
    for case_id, pid, kind, find, new, expect_check in FAULTS:
        original = text_of[pid]
        if original.count(find) != 1:
            raise ValueError(f"{case_id}: the text to change must appear exactly once in {pid}")
        rows.append({"case_id": case_id, "paragraph_id": pid, "fault_type": kind, "expected": "REJECT",
                     "expected_check": expect_check, "source": "hand-written", "verified": "no",
                     "change": f"{find}  ->  {new}", "original": original, "rewrite": original.replace(find, new)})
    for case_id, pid, find, new in CLEAN:
        original = text_of[pid]
        if original.count(find) != 1:
            raise ValueError(f"{case_id}: the text to change must appear exactly once in {pid}")
        rows.append({"case_id": case_id, "paragraph_id": pid, "fault_type": "clean rewrite", "expected": "ACCEPT",
                     "expected_check": "", "source": "hand-written", "verified": "no",
                     "change": f"{find}  ->  {new}", "original": original, "rewrite": original.replace(find, new)})
    # Real rewrites from the Sprint 2 V3 run. They passed the old checks but nobody has
    # confirmed the meaning is unchanged, so the expected label must be set by a person.
    if V3_FILE.exists():
        v3 = pd.read_csv(V3_FILE, keep_default_na=False)
        for i, r in enumerate(v3[v3.status == "revised"].itertuples(), 1):
            rows.append({"case_id": f"V{i}", "paragraph_id": r.pid, "fault_type": "real V3 rewrite",
                         "expected": "TO LABEL", "expected_check": "", "source": "Sprint 2 V3 run",
                         "verified": "no", "change": "whole paragraph rewritten",
                         "original": r.v0_text, "rewrite": r.v3_text})
    EVAL.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(CASES_FILE, index=False)
    print(f"Wrote {len(rows)} cases to {CASES_FILE}")


def run(llm=False, checker_model=None, token_limit=1_500_000, labelled_only=False):
    package, v0, _ = read_input(INPUTS)
    cases = pd.read_csv(CASES_FILE, keep_default_na=False)
    if labelled_only:
        cases = cases[cases.expected.isin(["REJECT", "ACCEPT"])]
    evidence_gate = semantic_gate = None
    out = EVAL / ("results_with_llm" if llm else "results_rules_only")
    if llm:
        if not checker_model:
            raise SystemExit("--llm needs --checker-model")
        from src.writing.preservation import SemanticGate
        from src.writing.providers import OpenAIJSON, TokenBudget
        from src.writing.storage import RunStore
        from datetime import datetime
        store = RunStore(out / datetime.now().strftime("calls-%Y%m%dT%H%M%S"))
        budget = TokenBudget(token_limit)
        evidence_gate = checks.EvidenceGate(OpenAIJSON(checker_model, budget, store, stage="evidence"),
                                            checks.EvidenceIndex(package))
        semantic_gate = SemanticGate(OpenAIJSON(checker_model, budget, store, stage="preservation"))
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for case in cases.itertuples():
        try:
            results = checks.check_rewrite(package, v0, v0, case.paragraph_id, case.rewrite,
                                           evidence_gate=evidence_gate, semantic_gate=semantic_gate)
        except Exception as error:  # e.g. the token budget ran out: keep what we have so far
            print(f"Stopped at {case.case_id}: {type(error).__name__}: {error}")
            break
        failed = [r for r in results if not r.passed]
        verdict = "REJECT" if failed else "ACCEPT"
        records.append({"case_id": case.case_id, "fault_type": case.fault_type, "expected": case.expected,
                        "verdict": verdict, "caught_by": failed[0].check if failed else "",
                        "reason": failed[0].reason if failed else "", "verified": case.verified,
                        "correct": "" if case.expected not in ("REJECT", "ACCEPT") else verdict == case.expected})
        print(f"{case.case_id:4s} {case.fault_type:22s} expected {case.expected:8s} got {verdict:6s} "
              f"{('(' + failed[0].check + ')') if failed else ''}")
    table = pd.DataFrame(records)
    table.to_csv(out / "case_results.csv", index=False)
    summary = summarise(table, llm)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out / "summary.md").write_text(as_markdown(summary), encoding="utf-8")
    print("\n" + as_markdown(summary))


def summarise(table, llm):
    by_type = {}
    for kind, group in table[table.expected == "REJECT"].groupby("fault_type", sort=False):
        caught = int((group.verdict == "REJECT").sum())
        by_type[kind] = {"caught": caught, "planted": len(group),
                         "by_check": group[group.verdict == "REJECT"].caught_by.value_counts().to_dict()}
    faults = table[table.expected == "REJECT"]
    clean = table[table.expected == "ACCEPT"]
    unlabelled = table[~table.expected.isin(["REJECT", "ACCEPT"])]
    return {
        "checks_used": "rules + evidence check + meaning check" if llm else "rules only (no model calls)",
        "fault_catch_rate": f"{int((faults.verdict == 'REJECT').sum())} of {len(faults)}",
        "false_alarms_on_clean_rewrites": f"{int((clean.verdict == 'REJECT').sum())} of {len(clean)}",
        "false_alarm_reasons": clean[clean.verdict == "REJECT"].reason.tolist(),
        "by_fault_type": by_type,
        "real_v3_rewrites_awaiting_labels": {"rejected": int((unlabelled.verdict == "REJECT").sum()),
                                             "accepted": int((unlabelled.verdict == "ACCEPT").sum())},
        "labels_verified_by_a_person": f"{int((table.verified == 'yes').sum())} of {len(table)}",
    }


def as_markdown(s):
    lines = [f"Checks used: {s['checks_used']}", "",
             f"Planted faults caught: **{s['fault_catch_rate']}**  ",
             f"False alarms on clean rewrites: **{s['false_alarms_on_clean_rewrites']}**", "",
             "| Fault type | Caught | Caught by |", "|---|---|---|"]
    for kind, v in s["by_fault_type"].items():
        by = ", ".join(f"{k} {n}" for k, n in v["by_check"].items()) or "none"
        lines.append(f"| {kind} | {v['caught']} of {v['planted']} | {by} |")
    lines += ["", f"Labels verified by a person: {s['labels_verified_by_a_person']}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["build", "run"])
    parser.add_argument("--llm", action="store_true", help="also run the evidence and meaning checks (API calls)")
    parser.add_argument("--checker-model", help="model ID for the evidence and meaning checks")
    parser.add_argument("--token-limit", type=int, default=1_500_000)
    parser.add_argument("--labelled-only", action="store_true", help="skip rows whose expected label is not set yet")
    args = parser.parse_args(argv)
    if args.step == "build":
        build()
    else:
        run(args.llm, args.checker_model, args.token_limit, args.labelled_only)


if __name__ == "__main__":
    sys.exit(main())
