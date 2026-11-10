"""External validation with GPTZero: does the revised text also look less AI-written to a detector we did not build?

Our pipeline lowers OUR detector's score, which it was guided by. GPTZero is independent of it,
so it tests whether the improvement generalises (and is not just our detector being beaten).

Two ways to run it:

  A) Web, free, no key (manual):
       python src/detection/gptzero_check.py export sprint2_demo/runs/half2-20261110-third
     writes gptzero_manual.csv next to the run: paste each `text` into https://gptzero.me,
     type the "AI" percentage into `ai_percent`, then
       python src/detection/gptzero_check.py summarise sprint2_demo/runs/half2-20261110-third

  B) API, needs GPTZERO_API_KEY in .env (paid plan):
       python src/detection/gptzero_check.py api sprint2_demo/runs/half2-20261110-third

Both score each revised paragraph before and after, plus the whole revised section as one
document (GPTZero is more reliable on longer text). Results: gptzero_results.json in the run folder.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
API_URL = "https://api.gptzero.me/v2/predict/text"
CITATION = re.compile(r"\s*(?:\[\[[^\]]+\]\]\s*;?\s*)+")


def plain(text):
    text = re.sub(r"\s+([.,;:])", r"\1", CITATION.sub(" ", text))
    return re.sub(r"([.!?])\.", r"\1", text).strip()


def items(run_dir):
    """Before/after texts for every revised paragraph, plus the joined section as one document."""
    report = json.loads((Path(run_dir) / "change_report.json").read_text(encoding="utf-8"))
    rows = []
    revised = [r for r in report["paragraphs"] if r["outcome"] == "revised"]
    for r in revised:
        for version, key, ours in (("before", "text_before", "score_before"), ("after", "text_after", "score_after")):
            rows.append({"item": r["paragraph_id"], "version": version, "our_score": round(r[ours], 1),
                         "words": len(plain(r[key]).split()), "text": plain(r[key])})
    if len(revised) > 1:
        for version, key in (("before", "text_before"), ("after", "text_after")):
            joined = "\n\n".join(plain(r[key]) for r in revised)
            rows.append({"item": "ALL (joined)", "version": version, "our_score": None,
                         "words": len(joined.split()), "text": joined})
    return rows


def export(run_dir):
    out = Path(run_dir) / "gptzero_manual.csv"
    table = pd.DataFrame(items(run_dir))
    table["ai_percent"] = ""
    table.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(table)} texts to {out}.\nPaste each `text` into https://gptzero.me and type its AI % into "
          "`ai_percent` (a number 0-100). Save as CSV UTF-8, then run the `summarise` step.")


def call_api(text, key, timeout=60):
    import urllib.request
    request = urllib.request.Request(API_URL, data=json.dumps({"document": text}).encode("utf-8"), method="POST",
                                     headers={"x-api-key": key, "Content-Type": "application/json",
                                              "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        doc = json.loads(response.read().decode("utf-8"))["documents"][0]
    return {"ai_percent": round(100 * doc["class_probabilities"]["ai"], 1),
            "mixed_percent": round(100 * doc["class_probabilities"].get("mixed", 0), 1),
            "predicted_class": doc.get("predicted_class"), "confidence": doc.get("confidence_category")}


def api(run_dir, caller=call_api):
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    key = os.environ.get("GPTZERO_API_KEY", "").strip()
    if not key and caller is call_api:
        raise SystemExit("Add GPTZERO_API_KEY=... to .env (never commit it), or use the free manual route.")
    rows = []
    for row in items(run_dir):
        result = caller(row["text"], key)
        rows.append({**row, **result})
        print(f"{row['item']:>13} {row['version']:6} ours {row['our_score']}  GPTZero AI {result['ai_percent']}%")
    table = pd.DataFrame(rows)
    table.to_csv(Path(run_dir) / "gptzero_api.csv", index=False, encoding="utf-8-sig")
    return summarise(run_dir, table, source="GPTZero API")


def summarise(run_dir, table=None, source="GPTZero website (manual)"):
    if table is None:
        table = pd.read_csv(Path(run_dir) / "gptzero_manual.csv", keep_default_na=False)
        if (table.ai_percent.astype(str).str.strip() == "").any():
            raise SystemExit("Some rows have no ai_percent yet.")
    table["ai_percent"] = table.ai_percent.astype(str).str.replace("%", "").str.strip().astype(float)
    table["our_score"] = pd.to_numeric(table.our_score, errors="coerce")
    wide = table.pivot(index="item", columns="version", values="ai_percent")
    paragraphs = wide.drop(index="ALL (joined)", errors="ignore")
    ours = table[table.item != "ALL (joined)"].pivot(index="item", columns="version", values="our_score")
    result = {
        "source": source,
        "paragraphs": int(len(paragraphs)),
        "gptzero_mean_ai_percent": {"before": round(float(paragraphs.before.mean()), 1),
                                    "after": round(float(paragraphs.after.mean()), 1)},
        "paragraphs_gptzero_lower_after": f"{int((paragraphs.after < paragraphs.before).sum())} of {len(paragraphs)}",
        "our_detector_mean": {"before": round(float(ours.before.mean()), 1), "after": round(float(ours.after.mean()), 1)},
        "joined_section_ai_percent": ({k: float(v) for k, v in wide.loc["ALL (joined)"].items()}
                                      if "ALL (joined)" in wide.index else None),
        "per_paragraph": {i: {"gptzero_before": float(r.before), "gptzero_after": float(r.after),
                              "ours_before": float(ours.loc[i, "before"]), "ours_after": float(ours.loc[i, "after"])}
                          for i, r in paragraphs.iterrows()},
        "note": "GPTZero is less reliable on short texts; the joined section is the steadier number. "
                "Both detectors are imperfect, so agreement in direction matters more than exact values.",
    }
    (Path(run_dir) / "gptzero_results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["export", "summarise", "api"])
    parser.add_argument("run_dir", type=Path, help="a pipeline run folder containing change_report.json")
    args = parser.parse_args(argv)
    {"export": export, "summarise": summarise, "api": api}[args.step](args.run_dir)


if __name__ == "__main__":
    sys.exit(main())
