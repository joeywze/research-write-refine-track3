"""Score held-out human and generated passages with one frozen detector."""

import argparse
import hashlib
import io
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score

from detector import score
from train_detector import paper_ids


def evaluate(model_path, human_path, generated_path, output):
    model_bytes = model_path.read_bytes()
    model = json.loads(model_bytes)
    training = set(paper_ids(model.get("training_paper_ids", [])))
    heldout = set(paper_ids(model.get("heldout_paper_ids", [])))
    if not training or not heldout or training & heldout:
        raise ValueError("Use a fitted detector with a disjoint, recorded paper split")
    tables, input_hashes = [], {}
    for label, kind, path in ((0, "human", human_path), (1, "generated", generated_path)):
        data = path.read_bytes()
        input_hashes[kind] = hashlib.sha256(data).hexdigest()
        frame = pd.read_csv(io.BytesIO(data), keep_default_na=False, dtype=str)
        if frame.empty or not {"paper_id", "text"} <= set(frame.columns) or frame["text"].str.strip().eq("").any():
            raise ValueError(f"{path.name} must contain non-empty paper_id and text columns")
        frame["paper_id"] = paper_ids(frame["paper_id"])
        frame["label"] = label
        tables.append(frame[["paper_id", "text", "label"]])
    passages = pd.concat(tables, ignore_index=True)
    actual = set(passages.paper_id)
    if actual & training:
        raise ValueError("Evaluation includes a source paper used to fit the detector")
    if actual != heldout:
        raise ValueError("Evaluation paper IDs must match the frozen holdout list")
    passages["score"] = [score(prose, model)["score"] for prose in passages.text]
    summary = {
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "input_sha256": input_hashes,
        "passage_auc": float(roc_auc_score(passages.label, passages.score)),
        "human_papers": int(tables[0].paper_id.nunique()),
        "generated_papers": int(tables[1].paper_id.nunique()),
        "human_passages": len(tables[0]),
        "generated_passages": len(tables[1]),
        "interpretation": "Passage-level authorship discrimination on supplied papers. "
                          "Check genre, prior exposure and corpus provenance before making generalisation claims.",
    }
    output.mkdir(parents=True, exist_ok=False)
    passages.to_csv(output / "scores.csv", index=False)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("model", "human", "generated", "output"):
        parser.add_argument("--" + arg, required=True, type=Path)
    args = parser.parse_args()
    try:
        summary = evaluate(args.model, args.human, args.generated, args.output)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
