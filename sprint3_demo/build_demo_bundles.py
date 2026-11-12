"""Pre-build everything the Sprint 3 demo site shows, one JSON file per topic.

The hosted site has no API key, so nothing is generated on the spot: this script collects, for each
of the five topics, the topic and its gap, the claims to review, the first draft (V0) and the final
paper from the saved pipeline run, with detector scores, check results and the scores of the real
papers the draft cites. The site only reads these files, so every topic opens instantly.

Run from the repo root after the final pipeline runs exist:
    python sprint3_demo/build_demo_bundles.py
    python sprint3_demo/build_demo_bundles.py --runs "half2-20261112-{topic}"   # another set of runs
Writes sprint3_demo/bundles/<topic>.json and sprint3_demo/bundles/index.json.
"""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "sprint2_demo"))
sys.path.insert(0, str(ROOT / "src" / "detection"))

import half2_pipeline as hp  # noqa: E402
import half2_checks as checks  # noqa: E402

TOPICS = ["cluster7", "cluster0", "cluster6", "cluster13", "cluster18"]
RUNS = ROOT / "sprint2_demo" / "runs"
OUT = HERE / "bundles"
ABSTRACTS = ROOT / "data" / "emnlp_2025_main.xlsx"
OOF = [ROOT / "evaluation-output" / "grouped_cv" / "detector_oof_predictions.csv",          # local (gitignored)
       ROOT / "results" / "detection" / "heldout_eval" / "detector_oof_predictions.csv"]  # committed copy, if any
INDEX = ROOT / "drafts" / "track3_five_topic_index.json"


def emnlp_id(url):
    """https://aclanthology.org/2025.emnlp-main.1065/ -> 2025.emnlp-main.1065 (None for other venues)."""
    m = re.search(r"(2025\.emnlp-main\.\d+)", url or "")
    return m[1] if m else None


def real_paper_scores(package, model, abstracts, oof):
    """Detector score of each cited EMNLP 2025 paper's abstract.

    Uses the out-of-fold score (from a model that never saw that paper) where there is one, otherwise
    the saved detector."""
    rows, seen = [], set()
    for s in package.sources:
        pid = emnlp_id(s.url)
        if not pid or pid not in abstracts or pid in seen:
            continue
        seen.add(pid)
        if pid in oof:
            score, basis = oof[pid], "unseen-paper model"
        else:
            score, basis = hp.score(abstracts[pid], model)["score"], "saved detector"
        rows.append({"source_id": s.source_id, "paper_id": pid, "title": s.title, "url": s.url,
                     "score": round(float(score), 1), "basis": basis})
    return rows


def claims_to_review(entry):
    """Claim, evidence quote, page and source link for each cited claim (provisional topics only)."""
    path = entry.get("fact_check_results")
    if not path or not (ROOT / path).exists():
        return []
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    out = []
    for i, r in enumerate(data.get("results", []), 1):
        out.append({"claim_id": f"{r['paragraph_id']}-{i}", "paragraph_id": r["paragraph_id"], "claim": r["claim"],
                    "evidence": [{"title": m.get("title", ""), "quote": m.get("evidence_quote", ""),
                                  "page": m.get("page", ""), "url": m.get("source_url", ""),
                                  "status": m.get("verification", "")} for m in r.get("matches", [])]})
    return out


def paragraphs(draft, manifest, model):
    editable = hp.editable_ids(manifest)
    rows = []
    for p in draft.paragraphs:
        scored = p.paragraph_id in editable and len(checks.plain(p.text).split()) >= hp.MIN_WORDS
        rows.append({"id": p.paragraph_id, "section": p.section, "text": p.text,
                     "score": round(hp.score(p.text, model)["score"], 1) if scored else None})
    return rows


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else None


def build_topic(topic, entry, model, abstracts, oof, run_name):
    package, v0, manifest, _, _ = hp.load_topic(topic)
    report = json.loads((RUNS / run_name.format(topic=topic) / "change_report.json").read_text(encoding="utf-8"))
    final = v0
    for r in report["paragraphs"]:
        if r["outcome"] == "revised":
            final = checks.with_paragraph(final, r["paragraph_id"], r["text_after"])
    v0_rows, final_rows = paragraphs(v0, manifest, model), paragraphs(final, manifest, model)
    real = real_paper_scores(package, model, abstracts, oof)
    reviewed = entry.get("status") == "REVIEWED_HANDOVER"
    records = [{k: r.get(k) for k in ("paragraph_id", "section", "score_before", "score_after", "outcome",
                                      "top_features", "critic_leads", "needs_human_edit", "held_reason")}
               | {"attempts": [{k: a.get(k) for k in ("attempt", "score", "accepted", "verdict", "checks")}
                               for a in r["attempts"]]}
               for r in report["paragraphs"]]
    return {
        "schema_version": 1, "id": topic, "title": package.title, "reviewed": reviewed,
        "status_label": "Reviewed by the team" if reviewed else "Claims not yet reviewed",
        "research_question": package.research_question, "gap": package.gap, "contribution": package.contribution,
        "claims": [] if reviewed else claims_to_review(entry),
        "real_papers": real,
        "real_band": {"n": len(real), "min": min((r["score"] for r in real), default=None),
                      "max": max((r["score"] for r in real), default=None), "mean": mean([r["score"] for r in real])},
        "v0": {"paragraphs": v0_rows, "mean": mean([p["score"] for p in v0_rows])},
        "final": {"paragraphs": final_rows, "mean": mean([p["score"] for p in final_rows])},
        "rewrite": {"threshold": report["threshold"], "totals": report["totals"], "paragraphs": records,
                    "critic": report.get("critic")},
        "manifest": {"layout": manifest["layout"],
                     "blocks": [{"paragraph_id": b["paragraph_id"], "citation_occurrences": b["citation_occurrences"]}
                                for b in manifest["blocks"]]},
        "source_run": run_name.format(topic=topic),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", default="half2-final-{topic}", help="run folder pattern in sprint2_demo/runs")
    args = parser.parse_args(argv)
    model = json.loads(hp.MODEL_FILE.read_text(encoding="utf-8"))
    table = pd.read_excel(ABSTRACTS)
    abstracts = dict(zip(table.paper_id.astype(str), table.abstract.astype(str)))
    found = next((f for f in OOF if f.exists()), None)
    oof = {}
    if found:
        o = pd.read_csv(found)
        oof = {p: 100 * float(v) for p, v in zip(o[o.label == 0].paper_id, o[o.label == 0].p_stylo)}
    else:
        print("Note: no paper-grouped out-of-fold scores found; real papers are scored with the saved detector.")
    entries = {t["id"]: t for t in json.loads(INDEX.read_text(encoding="utf-8"))["topics"]}
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for topic in TOPICS:
        bundle = build_topic(topic, entries[topic], model, abstracts, oof, args.runs)
        (OUT / f"{topic}.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        t = bundle["rewrite"]["totals"]
        index.append({"id": topic, "title": bundle["title"], "gap": bundle["gap"], "status_label": bundle["status_label"],
                      "reviewed": bundle["reviewed"]})
        print(f"{topic:10} V0 {bundle['v0']['mean']} -> final {bundle['final']['mean']} | real {bundle['real_band']} "
              f"| claims {len(bundle['claims'])} | rewritten {t['revised']}/{t['selected']} "
              f"| critic {(bundle['rewrite']['critic'] or {}).get('review_of_v0')}")
    (OUT / "index.json").write_text(json.dumps({"schema_version": 1, "topics": index}, ensure_ascii=False, indent=1) + "\n",
                                    encoding="utf-8")
    print(f"Wrote {len(index)} topic bundles to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
