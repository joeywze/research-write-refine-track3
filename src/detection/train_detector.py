"""
Fit and validate the stylometric detector.

Human class : real EMNLP 2025 abstracts (data/emnlp_2025_main.xlsx)
AI class    : paragraphs from data/generated/*.csv (all sections)

Design choices (see README "Detector"):
  1. Features are standardised against the human reference distribution.
  2. Each feature has a prior direction (e.g. more hedging = more AI-like).
     Weights are constrained to agree with that direction (>= 0 after
     orientation). Without this, the model learns that real abstracts use
     words like "robust" and "significant" more than our generator does,
     and the rewriting loop would then *reward* adding clichés.
  3. Genre features are reported but not scored. First-person "we" is the
     strongest single separator, but only because the human reference is
     abstracts (which nearly always say "we") while many AI paragraphs are
     related-work or method text (which often don't). Scoring it would
     penalise every related-work paragraph, human or not.
  4. Content features (numbers, parentheses/citations) are reported but not
     used for scoring: our generator was told not to invent numbers or
     citations, so those features measure the prompt, not the style, and a
     reviser optimising them would be pushed to fabricate.
  5. Validation splits AI text by *paper* (GroupKFold) so the same paper never
     appears in train and test.

Also fits a TF-IDF + logistic regression baseline to show why we don't use
it: it separates the classes almost perfectly from topic/genre words, and it
gives the reviser no actionable feedback.

Outputs: results/detector_model.json, results/detector_validation.json,
         results/feature_effects.csv
"""

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detector import FEATURE_NAMES, analyse, split_paragraphs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "detection"
RESULTS.mkdir(parents=True, exist_ok=True)

# +1: higher value = more AI-like; -1: higher value = more human-like
DIRECTION = {
    "sent_len_cv": -1,
    "short_sent_rate": -1,
    "long_sent_rate": -1,
    "hedge_per_100w": +1,
    "stacked_hedge_rate": +1,
    "ai_vocab_per_100w": +1,
    "ai_phrase_per_100w": +1,
    "promo_adj_per_100w": +1,
    "transition_open_rate": +1,
    "triplet_rate": +1,
    "emdash_per_100w": +1,
    "trigram_repeat": +1,
    "ttr": +1,
}
SCORING_FEATURES = list(DIRECTION)
REPORT_ONLY = [f for f in FEATURE_NAMES if f not in DIRECTION]
L2 = 1.0


def load_data(min_words: int = 60):
    human = pd.read_excel(ROOT / "data" / "emnlp_2025_main.xlsx")
    human = human[human["abstract"].astype(str).str.split().str.len() >= min_words]
    rows = [
        {"text": t, "label": 0, "group": f"h_{pid}", "section": "abstract", "paper_id": pid}
        for pid, t in zip(human["paper_id"], human["abstract"])
    ]
    for f in sorted(glob.glob(str(ROOT / "data" / "generated" / "*.csv"))):
        g = pd.read_csv(f, keep_default_na=False)
        for _, r in g.iterrows():
            for p in split_paragraphs(r["text"], min_words):
                rows.append({"text": p, "label": 1, "group": f"a_{r['paper_id']}",
                             "section": r["section"], "paper_id": r["paper_id"]})
    df = pd.DataFrame(rows)
    feats = pd.DataFrame([analyse(t).features for t in df["text"]])
    return pd.concat([df.reset_index(drop=True), feats], axis=1)


def fit_monotone(X: np.ndarray, y: np.ndarray, l2: float = L2):
    """Logistic regression with non-negative coefficients (bounded L-BFGS)."""
    n, d = X.shape
    w_pos = 0.5 / y.mean()
    w_neg = 0.5 / (1 - y.mean())
    sw = np.where(y == 1, w_pos, w_neg)

    def loss(theta):
        b, w = theta[0], theta[1:]
        z = b + X @ w
        p = 1 / (1 + np.exp(-z))
        eps = 1e-9
        ll = -(sw * (y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))).sum() / n
        grad_z = sw * (p - y) / n
        g = np.concatenate([[grad_z.sum()], X.T @ grad_z + l2 * w / n])
        return ll + 0.5 * l2 * (w @ w) / n, g

    bounds = [(None, None)] + [(0, None)] * d
    res = minimize(loss, np.zeros(d + 1), jac=True, method="L-BFGS-B", bounds=bounds)
    return res.x[0], res.x[1:]


def standardise(df_train_h: pd.DataFrame):
    mean = {f: float(df_train_h[f].mean()) for f in FEATURE_NAMES}
    std = {f: float(df_train_h[f].std() or 1.0) for f in FEATURE_NAMES}
    return mean, std


def design(df, mean, std):
    cols = []
    for f in SCORING_FEATURES:
        z = ((df[f] - mean[f]) / std[f]).clip(-6, 6)
        cols.append(DIRECTION[f] * z)
    return np.vstack(cols).T


def main():
    df = load_data()
    print(f"Human abstracts: {(df.label == 0).sum()}   AI paragraphs: {(df.label == 1).sum()} "
          f"from {df[df.label == 1].paper_id.nunique()} papers")

    # ---------------- cross-validation, grouped by paper ----------------
    gkf = GroupKFold(n_splits=5)
    oof = np.zeros(len(df))
    oof_tfidf = np.zeros(len(df))
    for tr, te in gkf.split(df, df.label, df.group):
        dtr, dte = df.iloc[tr], df.iloc[te]
        mean, std = standardise(dtr[dtr.label == 0])
        b, w = fit_monotone(design(dtr, mean, std), dtr.label.values)
        oof[te] = 1 / (1 + np.exp(-(b + design(dte, mean, std) @ w)))

        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        clf = LogisticRegression(max_iter=2000, class_weight="balanced")
        clf.fit(vec.fit_transform(dtr.text), dtr.label)
        oof_tfidf[te] = clf.predict_proba(vec.transform(dte.text))[:, 1]

    df["p_stylo"], df["p_tfidf"] = oof, oof_tfidf
    val = {
        "n_human": int((df.label == 0).sum()),
        "n_ai": int((df.label == 1).sum()),
        "auc_stylometric_all": round(roc_auc_score(df.label, df.p_stylo), 3),
        "auc_tfidf_all": round(roc_auc_score(df.label, df.p_tfidf), 3),
    }
    # Like-for-like check: AI abstracts vs human abstracts only
    abs_mask = df.section == "abstract"
    if df[abs_mask].label.nunique() == 2:
        val["n_ai_abstracts"] = int(df[abs_mask].label.sum())
        val["auc_stylometric_abstract_only"] = round(roc_auc_score(df[abs_mask].label, df[abs_mask].p_stylo), 3)
        val["auc_tfidf_abstract_only"] = round(roc_auc_score(df[abs_mask].label, df[abs_mask].p_tfidf), 3)
    acc = ((df.p_stylo > 0.5) == df.label).mean()
    val["accuracy_stylometric_at_0.5"] = round(float(acc), 3)
    val["mean_score_by_section"] = (
        df.groupby(np.where(df.label == 0, "HUMAN abstract", "AI " + df.section)).p_stylo.mean()
        .mul(100).round(1).to_dict()
    )

    # ---------------- final model on all data ----------------
    mean, std = standardise(df[df.label == 0])
    b, w = fit_monotone(design(df, mean, std), df.label.values)
    model = {
        "intercept": float(b),
        "features": SCORING_FEATURES,
        # fold orientation into the coefficient so score() can use raw z
        "coef": {f: float(DIRECTION[f] * wi) for f, wi in zip(SCORING_FEATURES, w)},
        "mean": mean,
        "std": std,
        "reference": "EMNLP 2025 main abstracts",
    }
    (RESULTS / "detector_model.json").write_text(json.dumps(model, indent=2))
    (RESULTS / "detector_validation.json").write_text(json.dumps(val, indent=2))

    effects = []
    for f in FEATURE_NAMES:
        h, a = df[df.label == 0][f], df[df.label == 1][f]
        effects.append({
            "feature": f,
            "human_mean": round(h.mean(), 4),
            "ai_mean": round(a.mean(), 4),
            "cohens_d": round((a.mean() - h.mean()) / h.std(), 2),
            "used_in_score": f in DIRECTION,
            "weight": round(model["coef"].get(f, 0.0), 3),
        })
    pd.DataFrame(effects).sort_values("cohens_d").to_csv(RESULTS / "feature_effects.csv", index=False)
    df[["paper_id", "section", "label", "p_stylo", "p_tfidf", "text"]].to_csv(
        RESULTS / "detector_oof_predictions.csv", index=False)

    print(json.dumps(val, indent=2))
    print("\nWeights (sign = direction; 0 = data disagreed with the prior):")
    for f, c in sorted(model["coef"].items(), key=lambda kv: -abs(kv[1])):
        print(f"  {f:22s} {c:+.3f}")


if __name__ == "__main__":
    main()
