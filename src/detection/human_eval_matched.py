"""Human study, version 2: can people tell human-written paper text from AI-written text?

Builds a balanced, reproducible set of short paragraphs for a Google Form:
  * N real paragraphs written by people (EMNLP 2025 papers)  -> condition "real"
  * N AI-generated paragraphs (data/generated: LLM-written sections) -> condition "generated"

Both sides go through the SAME rules so that nothing but the writer differs:
  * 50-80 words, made of whole sentences (the opening sentences of a paragraph or abstract)
  * no citations, years, "et al.", reference numbers, tables, figures, equations or links
  * no PDF debris (run-together words, broken hyphenation)
  * half from abstracts and half from body sections on each side, so genre is not a tell
  * at most one paragraph per paper, and no paper appears on both sides
A fixed seed makes the selection reproducible.

Outputs
  .private/human_eval_v2/PRIVATE_answer_key.csv   (gitignored: never show it to raters)
  results/detection/human_eval_v2/form_for_raters.md
Then build the Google Form and, later, score the responses:
  python src/detection/make_google_form.py --key .private/human_eval_v2/PRIVATE_answer_key.csv --out results/detection/human_eval_v2
  python src/detection/human_eval.py score responses.csv --key .private/human_eval_v2/PRIVATE_answer_key.csv --out results/detection/human_eval_v2

Usage
  python src/detection/human_eval_matched.py            # 10 real + 10 generated
  python src/detection/human_eval_matched.py --n 8      # 8 + 8
"""

import argparse
import glob
from pathlib import Path
import random
import re
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from human_eval import tidy  # noqa: E402  (same clean-up as version 1)

KEY_DIR = ROOT / ".private" / "human_eval_v2"
FORM_DIR = ROOT / "results" / "detection" / "human_eval_v2"
SEED = 17
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
# Anything that would give away a real paper (or is simply broken text) is excluded on both sides.
TELLS = re.compile(
    r"\[\d+|\bet al\b|\b(19|20)\d{2}\b|\b(Table|Figure|Fig\.|Appendix|Section|Eq\.)\s*\d*|§|=|https?:|"
    r"\b[a-z]+[A-Z][a-z]+\b|\w- \w|[{}<>]|\b(\w+) \3\b|@")
BODY = {"introduction", "related_work", "methodology", "experiments", "conclusion", "body"}


def window(text, low=50, high=80):
    """The opening whole sentences of a passage that add up to low-high words, or None."""
    words, out = 0, []
    for sentence in SENTENCE.split(tidy(text)):
        out.append(sentence)
        words += len(sentence.split())
        if words >= low:
            return " ".join(out) if words <= high else None
    return None


def usable(text):
    return text is not None and text.endswith(".") and not TELLS.search(text)


def human_pool(low, high, exclude):
    rows = []
    abstracts = pd.read_excel(ROOT / "data" / "emnlp_2025_main.xlsx")
    for r in abstracts.itertuples():
        text = window(str(r.abstract), low, high)
        if str(r.paper_id) not in exclude and usable(text):
            rows.append({"paper_id": str(r.paper_id), "section": "abstract", "text": text})
    body = ROOT / "results" / "detection" / "heldout_fulltext_passages.csv"
    if body.exists():
        for r in pd.read_csv(body, keep_default_na=False).itertuples():
            text = window(r.text, low, high)
            if str(r.paper_id) not in exclude and usable(text):
                rows.append({"paper_id": str(r.paper_id), "section": "body", "text": text})
    return pd.DataFrame(rows)


def ai_pool(low, high):
    from detector import split_paragraphs
    rows = []
    for file in sorted(glob.glob(str(ROOT / "data" / "generated" / "*.csv"))):
        for r in pd.read_csv(file, keep_default_na=False).itertuples():
            for paragraph in split_paragraphs(r.text, 1):
                text = window(paragraph, low, high)
                if usable(text):
                    rows.append({"paper_id": str(r.paper_id), "section": r.section, "text": text})
    return pd.DataFrame(rows)


def pick(pool, n, rng):
    """n paragraphs, half abstracts and half body text, at most one per paper."""
    halves = {"abstract": n // 2, "body": n - n // 2}
    chosen, used = [], set()
    for kind, count in halves.items():
        part = pool[(pool.section == "abstract") == (kind == "abstract")]
        rows = part.to_dict("records")
        rng.shuffle(rows)
        taken = 0
        for row in rows:
            if taken == count:
                break
            if row["paper_id"] not in used:
                chosen.append(row)
                used.add(row["paper_id"])
                taken += 1
        if taken < count:
            raise SystemExit(f"Only {taken} usable {kind} paragraphs on one side; lower --n.")
    return chosen


def build(n=10, low=50, high=80, seed=SEED):
    rng = random.Random(seed)
    ai = ai_pool(low, high)
    human = human_pool(low, high, exclude=set(ai.paper_id))
    print(f"Usable paragraphs: {len(human)} real ({(human.section == 'abstract').sum()} abstracts), "
          f"{len(ai)} generated ({(ai.section == 'abstract').sum()} abstracts)")
    items = ([{**r, "condition": "real"} for r in pick(human, n, rng)]
             + [{**r, "condition": "generated"} for r in pick(ai, n, rng)])
    rng.shuffle(items)

    from detector import score as detector_score
    key, form = [], ["# Real or generated?\n",
                     "Each paragraph below is either from a published EMNLP 2025 paper or was generated by an "
                     "LLM. Citations were removed from all of them. For each one choose **Real paper** or "
                     "**Generated**, and how confident you are (1 = guess, 5 = certain).\n"]
    for i, item in enumerate(items, 1):
        iid = f"Item {i:02d}"
        key.append({"item_id": iid, "truth": "real" if item["condition"] == "real" else "generated",
                    "condition": item["condition"], "source": item["paper_id"], "section": item["section"],
                    "words": len(item["text"].split()), "detector_score": detector_score(item["text"])["score"],
                    "text": item["text"]})
        form.append(f"## {iid}\n\n{item['text']}\n\n- [ ] Real paper   - [ ] Generated   "
                    "Confidence 1-5: ___   What helped you decide: ________\n")
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    FORM_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(key).to_csv(KEY_DIR / "PRIVATE_answer_key.csv", index=False, encoding="utf-8-sig")
    (FORM_DIR / "form_for_raters.md").write_text("\n".join(form), encoding="utf-8")
    table = pd.DataFrame(key)
    print(table.groupby(["condition", "section"]).agg(items=("item_id", "count"), words=("words", "mean"),
                                                      detector=("detector_score", "mean")).round(1).to_string())
    print(f"\nAnswer key (private): {KEY_DIR.relative_to(ROOT)}/PRIVATE_answer_key.csv")
    print(f"Form text for raters:  {FORM_DIR.relative_to(ROOT)}/form_for_raters.md")
    return table


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", type=int, default=10, help="paragraphs per side (default 10 real + 10 generated)")
    parser.add_argument("--min-words", type=int, default=50)
    parser.add_argument("--max-words", type=int, default=80)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)
    build(args.n, args.min_words, args.max_words, args.seed)


if __name__ == "__main__":
    main()
